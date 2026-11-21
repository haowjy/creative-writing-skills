/*
 * How a level's arrows run between its boxes and where their labels sit: orthogonal connector
 * routing on a lane grid (route-grid.js holds the grid and the search). Arrows are routed one at a
 * time, the numbered path first, each against everything the earlier ones hold, and an arrow is
 * committed only with a label place of its own: a straight run of the finished route where the
 * label touches no box, frame title or border, other label or other arrow. When the cheapest route
 * has no such run, the route is rebuilt to pass through one (a straight run chosen first, then the
 * route to and from it), nearest the direct way first. So the clearances hold for whatever is
 * routed; they are not repaired afterwards. If no route exists (boxes drawn on top of each other),
 * the arrow is a straight line and `exact` is false. No DOM.
 */

import { MEMBER_OUTLINE } from "./frames.js";
import { CLEAR, createGrid, D, R } from "./route-grid.js";

const ROUND = 10;
/** Room a label keeps from the ends of its run: a bend, a rounded corner or an arrowhead. */
const LABEL_MARGIN = 10;
const LABEL_APART = 2;
const ANCHOR_TRIES = 14;
const ANCHOR_SAMPLES = 6000;
const RESTARTS = 5;

const overlap = (a, b, gap = 0) =>
  a.x < b.x + b.w + gap && b.x < a.x + a.w + gap && a.y < b.y + b.h + gap && b.y < a.y + a.h + gap;

function roundedPath(points) {
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let k = 1; k < points.length - 1; k++) {
    const [a, b, c] = points.slice(k - 1, k + 2);
    const r = Math.min(ROUND, Math.hypot(b.x - a.x, b.y - a.y) / 2, Math.hypot(c.x - b.x, c.y - b.y) / 2);
    const toward = (p) => {
      const len = Math.hypot(p.x - b.x, p.y - b.y) || 1;
      return { x: b.x + ((p.x - b.x) / len) * r, y: b.y + ((p.y - b.y) / len) * r };
    };
    const [p, q] = [toward(a), toward(c)];
    d += ` L ${p.x} ${p.y} Q ${b.x} ${b.y} ${q.x} ${q.y}`;
  }
  const last = points.at(-1);
  return `${d} L ${last.x} ${last.y}`;
}

/** The corners of a polyline given by every node it passes. */
function corners(points) {
  const out = [];
  for (const p of points) {
    const prev = out.at(-1);
    if (prev && prev.x === p.x && prev.y === p.y) continue;
    out.push(p);
    while (out.length > 2) {
      const [a, b, c] = out.slice(-3);
      if ((a.x === b.x && b.x === c.x) || (a.y === b.y && b.y === c.y)) out.splice(-2, 1);
      else break;
    }
  }
  return out;
}

/** True when a route of grid states passes through any node twice (a bend holds one node for several states). */
function revisits(states) {
  const nodes = states.map((s) => s >> 2).filter((n, k, all) => k === 0 || n !== all[k - 1]);
  return new Set(nodes).size !== nodes.length;
}

/** One pass over the arrows in `order`. */
function routeOnce({ boxes, frames = [], arrows }, order) {
  const list = [...boxes].map(([id, r]) => ({ id, ...r }));
  const byId = new Map(list.map((b) => [b.id, b]));
  const outlines = frames.flatMap((f) => f.outlines);
  const grid = createGrid({
    boxes: list,
    titles: frames.map((f) => f.title),
    outlines,
    frames: frames.filter((f) => f.solid).map((f) => f.outlines[0]),
  });
  const { pitch } = grid;
  const borders = outlines.flatMap((o) => [
    { x: o.x - 2, y: o.y - 2, w: o.w + 4, h: 4 },
    { x: o.x - 2, y: o.y + o.h - 2, w: o.w + 4, h: 4 },
    { x: o.x - 2, y: o.y, w: 4, h: o.h },
    { x: o.x + o.w - 2, y: o.y, w: 4, h: o.h },
  ]);
  const fixed = [...list, ...frames.map((f) => f.title), ...borders];
  const labels = [];
  const segments = [];

  /** Whether `rect` is clear of everything a label must stay off; `own` is this arrow's route, `host` the run the label sits on. */
  function labelFree(rect, own, host) {
    if (list.some((b) => overlap(rect, b, CLEAR))) return false;
    if (fixed.some((r) => overlap(rect, r, LABEL_APART))) return false;
    if (labels.some((r) => overlap(rect, r, LABEL_APART))) return false;
    const hits = (a, b) =>
      Math.min(a.x, b.x) <= rect.x + rect.w + 1 &&
      Math.max(a.x, b.x) >= rect.x - 1 &&
      Math.min(a.y, b.y) <= rect.y + rect.h + 1 &&
      Math.max(a.y, b.y) >= rect.y - 1;
    if (segments.some(([a, b]) => hits(a, b))) return false;
    for (let k = 1; k < own.length; k++) if (k !== host && hits(own[k - 1], own[k])) return false;
    return true;
  }

  /** The best free place for a label of `size` on one run of `points`, or null. */
  function placeLabel(points, size) {
    const w = size.width;
    const h = size.height;
    const lengths = [0];
    for (let k = 1; k < points.length; k++)
      lengths.push(lengths[k - 1] + Math.abs(points[k].x - points[k - 1].x) + Math.abs(points[k].y - points[k - 1].y));
    const whole = lengths.at(-1);
    let best = null;
    for (let k = 1; k < points.length; k++) {
      const [a, b] = [points[k - 1], points[k]];
      const flat = a.y === b.y;
      const lo = (flat ? Math.min(a.x, b.x) : Math.min(a.y, b.y)) + (flat ? w : h) / 2 + LABEL_MARGIN;
      const hi = (flat ? Math.max(a.x, b.x) : Math.max(a.y, b.y)) - (flat ? w : h) / 2 - LABEL_MARGIN;
      if (lo > hi) continue;
      const mid = (lo + hi) / 2;
      for (let step = 0; ; step += 4) {
        for (const c of step ? [mid - step, mid + step] : [mid]) {
          if (c < lo || c > hi) continue;
          const rect = flat ? { x: c - w / 2, y: a.y - h / 2, w, h } : { x: a.x - w / 2, y: c - h / 2, w, h };
          const along = lengths[k - 1] + Math.abs(flat ? c - a.x : c - a.y);
          const score = Math.abs(along / whole - 0.5) * 100 + (flat ? 0 : 8) + step * 0.05;
          if ((!best || score < best.score) && labelFree(rect, points, k)) best = { rect, score };
        }
        if (step > hi - lo) break;
      }
    }
    return best?.rect ?? null;
  }

  /** The route from `A` to `B` with no label constraint: { states, start, goal } or null. */
  function plain(starts, goals) {
    const states = grid.search(starts, goals);
    if (!states) return null;
    return { states, start: starts.find((p) => p.state === states[0]), goal: goals.get(states.at(-1)).port };
  }

  /** A route through a straight run of its own for the label: tries the runs nearest the direct way. */
  function viaRun(starts, goals, size, centres) {
    const { x0, y0, x1, y1 } = grid.bounds;
    const stride = Math.max(2, Math.ceil(Math.sqrt(((x1 - x0) * (y1 - y0)) / (pitch * pitch * ANCHOR_SAMPLES))));
    const candidates = [];
    for (const flat of [true, false]) {
      const along = flat ? size.width : size.height;
      const lanes = Math.ceil((along / 2 + LABEL_MARGIN) / pitch);
      for (let y = y0; y <= y1; y += stride * pitch)
        for (let x = x0; x <= x1; x += stride * pitch) {
          const detour = centres.reduce((sum, c) => sum + Math.abs(c.x - x) + Math.abs(c.y - y), 0);
          candidates.push({ x, y, flat, lanes, detour: detour + (flat ? 0 : 20) });
        }
    }
    candidates.sort((a, b) => a.detour - b.detour);
    let tries = 0;
    for (const c of candidates) {
      if (tries >= ANCHOR_TRIES) break;
      const rect = { x: c.x - size.width / 2, y: c.y - size.height / 2, w: size.width, h: size.height };
      const run = [];
      for (let k = -c.lanes; k <= c.lanes; k++)
        run.push(c.flat ? { x: c.x + k * pitch, y: c.y } : { x: c.x, y: c.y + k * pitch });
      if (!run.every((p) => grid.free(p.x, p.y, c.flat ? 1 : 2))) continue;
      if (!labelFree(rect, [], -1)) continue;
      const forward = c.flat ? R : D;
      const order = centres[0] && (c.flat ? centres[0].x > c.x : centres[0].y > c.y) ? [1, -1] : [-1, 1];
      for (const way of order) {
        const dir = way === -1 ? forward : forward ^ 2;
        const [first, last] = way === -1 ? [run[0], run.at(-1)] : [run.at(-1), run[0]];
        const middle = (way === -1 ? run : [...run].reverse()).slice(1, -1).map((p) => grid.stateAt(p.x, p.y, dir));
        const startState = grid.stateAt(first.x, first.y, dir);
        const endState = grid.stateAt(last.x, last.y, dir);
        tries++;
        const held = grid.holdRect(rect);
        const one = grid.search(starts, new Map([[startState, { port: null }]]));
        if (!one) {
          grid.release(held);
          continue;
        }
        const prefix = [...one, ...middle, endState];
        const mark = grid.hold(prefix, false);
        const two = grid.search([{ state: endState, g: 0 }], goals);
        grid.release(mark);
        const states = two && [...one, ...middle, ...two];
        grid.release(held);
        // A route that doubles back over its own nodes (a port off the run's line turns twice to reach
        // the run) would drop the run's first nodes when straightened, and the label would lose its margin.
        if (!states || revisits(states)) continue;
        return {
          states,
          start: starts.find((p) => p.state === one[0]),
          goal: goals.get(two.at(-1)).port,
          rect,
        };
      }
    }
    return null;
  }

  const results = new Array(arrows.length);
  const centreOf = (b) => ({ x: b.x + b.w / 2, y: b.y + b.h / 2 });

  for (const index of order) {
    const arrow = arrows[index];
    const A = byId.get(arrow.from);
    const B = byId.get(arrow.to);
    const size = arrow.label;
    grid.begin(A === B ? [A] : [A, B]);
    const others = list.filter((b) => b !== A && b !== B);
    const starts = grid.ports(A, others);
    const goals = new Map(
      grid.ports(B, others).map((p) => [(p.state >> 2) * 4 + (p.dir ^ 2), { extra: p.g, port: p }]),
    );
    let found = plain(starts, goals);
    let rect = null;
    let points = null;
    if (found) {
      points = corners([{ x: found.start.x, y: found.start.y }, ...found.states.map((s) => grid.point(s)), { x: found.goal.x, y: found.goal.y }]);
      if (size) {
        rect = placeLabel(points, size);
        if (!rect) {
          const centres = [centreOf(A), centreOf(B)];
          const via = viaRun(starts, goals, size, centres);
          if (via) {
            found = via;
            rect = via.rect;
            points = corners([{ x: via.start.x, y: via.start.y }, ...via.states.map((s) => grid.point(s)), { x: via.goal.x, y: via.goal.y }]);
          }
        }
      }
    }
    grid.end();
    if (!found) {
      const [p, q] = [centreOf(A), centreOf(B)];
      const horizontal = Math.abs(p.x - q.x) > Math.abs(p.y - q.y);
      const pt = (b, o) =>
        horizontal ? { x: o.x > centreOf(b).x ? b.x + b.w : b.x, y: centreOf(b).y } : { x: centreOf(b).x, y: o.y > centreOf(b).y ? b.y + b.h : b.y };
      results[index] = { points: [pt(A, q), pt(B, p)], label: null, exact: false };
      continue;
    }
    grid.hold(found.states, arrow.step !== null);
    if (rect) {
      grid.holdRect(rect);
      labels.push(rect);
    }
    for (let k = 1; k < points.length; k++) segments.push([points[k - 1], points[k]]);
    results[index] = { points, label: rect, exact: !size || Boolean(rect) };
  }

  let bounds = { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
  const grow = (x0, y0, x1, y1) => {
    bounds = { x0: Math.min(bounds.x0, x0), y0: Math.min(bounds.y0, y0), x1: Math.max(bounds.x1, x1), y1: Math.max(bounds.y1, y1) };
  };
  for (const r of [...list, ...outlines, ...frames.map((f) => f.title), ...labels]) grow(r.x, r.y, r.x + r.w, r.y + r.h);
  for (const r of results) {
    for (const p of r.points) grow(p.x, p.y, p.x, p.y);
    r.d = roundedPath(r.points);
  }
  return { arrows: results, bounds };
}

/** The order arrows are routed in: the numbered path first, then the shortest first. */
function priority({ boxes, arrows }) {
  const centre = (id) => ({ x: boxes.get(id).x + boxes.get(id).w / 2, y: boxes.get(id).y + boxes.get(id).h / 2 });
  const span = (e) => {
    const [p, q] = [centre(e.from), centre(e.to)];
    return Math.abs(p.x - q.x) + Math.abs(p.y - q.y);
  };
  return arrows
    .map((_, i) => i)
    .sort((i, j) => {
      const [a, b] = [arrows[i], arrows[j]];
      if ((a.step === null) !== (b.step === null)) return a.step === null ? 1 : -1;
      if (a.step !== null && a.step !== b.step) return a.step - b.step;
      return span(a) - span(b) || i - j;
    });
}

/**
 * Routes a level. `boxes` maps id → { x, y, w, h }; `frames` are [{ outlines: [rect], title: rect,
 * solid }] (a frame broken by a dragged-in box has one outline per member, and is not `solid`);
 * `arrows` are [{ from, to, label: { width, height } | null, step: number | null }].
 * Returns { arrows: [{ points, d, label: rect | null, exact }], bounds }, in the order of `arrows`.
 * An arrow that finds no route, or no label place, is routed again first, ahead of the rest:
 * earlier arrows and labels can wall a crowded box in.
 */
export function routeArrows(input) {
  let order = priority(input);
  let best = null;
  for (let round = 0; round < RESTARTS; round++) {
    const routed = routeOnce(input, order);
    const failed = routed.arrows.flatMap((a, i) => (a.exact ? [] : [i]));
    if (!best || failed.length < best.failed) best = { routed, failed: failed.length };
    if (!failed.length) break;
    order = [...failed, ...order.filter((i) => !failed.includes(i))];
  }
  return best.routed;
}

/**
 * What the router is given for a level as the viewer draws it: `rects` of the boxes, `frames` from
 * frameShapes, the page's `edges` and `noteLinks`, and `labelSize(edge)` → { width, height }.
 */
export function levelInput({ rects, frames, edges, noteLinks, labelSize }) {
  return {
    boxes: rects,
    frames: [...frames.values()].map((f) => ({
      outlines: f.fractured
        ? f.members.map((m) => ({
            x: f.x + m.x - MEMBER_OUTLINE,
            y: f.y + m.y - MEMBER_OUTLINE,
            w: m.w + 2 * MEMBER_OUTLINE,
            h: m.h + 2 * MEMBER_OUTLINE,
          }))
        : [{ x: f.x, y: f.y, w: f.w, h: f.h }],
      title: f.title,
      solid: !f.fractured,
    })),
    arrows: [
      ...edges.map((e) => ({ from: e.from, to: e.to, label: e.label ? labelSize(e) : null, step: e.step })),
      ...noteLinks.map((l) => ({ from: l.from, to: l.to, label: null, step: null })),
    ],
  };
}

/** Routes a level as the viewer draws it: { arrows (one per edge), links (one per note link), bounds }. */
export function routeLevel(level) {
  const { arrows, bounds } = routeArrows(levelInput(level));
  return { arrows: arrows.slice(0, level.edges.length), links: arrows.slice(level.edges.length), bounds };
}
