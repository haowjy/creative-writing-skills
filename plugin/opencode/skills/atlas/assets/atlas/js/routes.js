/*
 * How a level's arrows run between the boxes where they are now, a drag included, and where their
 * labels go. layout.js says how an arrow was meant to run (along the row, arcing over or under it,
 * or wrapping to the next row); while its two boxes still sit that way it runs so, and otherwise it
 * curves from the sides that face each other. Labels never cover a box or another label: a
 * numbered one tries places along its arrow, a side one that finds no room is left out (the panel
 * lists every arrow). No DOM.
 */

const ALONG = [0.5, 0.42, 0.58, 0.34, 0.66, 0.26, 0.74, 0.18, 0.82];
const ROUND = 10;
const WRAP_CLEAR = 24;

const NORMAL = { top: [0, -1], bottom: [0, 1], left: [-1, 0], right: [1, 0] };

const cx = (r) => r.x + r.w / 2;
const cy = (r) => r.y + r.h / 2;
const overlaps = (a, b, gap) =>
  a.x < b.x + b.w + gap && b.x < a.x + a.w + gap && a.y < b.y + b.h + gap && b.y < a.y + a.h + gap;

function facing(S, T) {
  if (T.y >= S.y + S.h + 12) return ["bottom", "top"];
  if (T.y + T.h <= S.y - 12) return ["top", "bottom"];
  return cx(T) > cx(S) ? ["right", "left"] : ["left", "right"];
}

/** How an arrow from box S to box T runs now: { kind, sides }, kind "line" | "arc" | "wrap" | "curve". */
function shapeOf(S, T, hint) {
  const sameRow = Math.abs(cy(S) - cy(T)) < Math.max(S.h, T.h) / 2;
  if (hint?.kind === "row" && sameRow)
    return { kind: "line", sides: cx(T) > cx(S) ? ["right", "left"] : ["left", "right"] };
  if (hint?.kind === "arc" && sameRow)
    return {
      kind: "arc",
      sides: hint.side === "above" ? ["top", "top"] : ["bottom", "bottom"],
      depth: hint.depth,
      up: hint.side === "above",
    };
  if (hint?.kind === "wrap" && S.y + S.h < hint.lane && hint.lane < T.y)
    return { kind: "wrap", sides: ["right", "left"], lane: hint.lane };
  return { kind: "curve", sides: facing(S, T) };
}

/** Spreads the arrows that leave one side of a box along it, in the order of where they go. */
function assignPorts(lines, rects) {
  const groups = new Map();
  lines.forEach((line, i) => {
    for (const end of [0, 1]) {
      const key = `${line.ids[end]}:${line.shape.sides[end]}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push({ i, end, other: rects.get(line.ids[1 - end]) });
    }
  });
  for (const [key, ends] of groups) {
    const side = key.slice(key.lastIndexOf(":") + 1);
    const box = rects.get(lines[ends[0].i].ids[ends[0].end]);
    const vertical = side === "top" || side === "bottom";
    ends.sort(
      (a, b) => (vertical ? cx(a.other) - cx(b.other) : cy(a.other) - cy(b.other)) || a.i - b.i,
    );
    const length = vertical ? box.w : box.h;
    const spacing = Math.min(16, (length * 0.8) / ends.length);
    ends.forEach((end, k) => {
      const off = (k - (ends.length - 1) / 2) * spacing;
      const [nx, ny] = NORMAL[side];
      const point = vertical
        ? { x: cx(box) + off, y: side === "top" ? box.y : box.y + box.h }
        : { x: side === "left" ? box.x : box.x + box.w, y: cy(box) + off };
      lines[end.i].ports[end.end] = { ...point, nx, ny, off };
    });
  }
}

function cubicPoints(p0, c1, c2, p3) {
  const points = [];
  for (let k = 0; k <= 24; k++) {
    const t = k / 24;
    const u = 1 - t;
    const at = (a, b, c, d) =>
      u * u * u * a + 3 * u * u * t * b + 3 * u * t * t * c + t * t * t * d;
    points.push({ x: at(p0.x, c1.x, c2.x, p3.x), y: at(p0.y, c1.y, c2.y, p3.y) });
  }
  return points;
}

function roundedPath(points) {
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let k = 1; k < points.length - 1; k++) {
    const [a, b, c] = points.slice(k - 1, k + 2);
    const r = Math.min(
      ROUND,
      Math.hypot(b.x - a.x, b.y - a.y) / 2,
      Math.hypot(c.x - b.x, c.y - b.y) / 2,
    );
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

/** The SVG path of one arrow and the points along it that its label may sit on. */
function draw(line, rects) {
  const [p0, p3] = line.ports;
  const { shape } = line;
  if (shape.kind === "wrap") {
    const [S, T] = line.ids.map((id) => rects.get(id));
    const lane = shape.lane + p0.off;
    const within = (y0, y1) => [...rects.values()].filter((r) => r.y < y1 && r.y + r.h > y0);
    const right =
      Math.max(S.x + S.w, ...within(p0.y, lane).map((r) => r.x + r.w)) + WRAP_CLEAR + p0.off;
    const left = Math.min(T.x, ...within(lane, p3.y).map((r) => r.x)) - WRAP_CLEAR + p0.off;
    const points = [
      p0,
      { x: right, y: p0.y },
      { x: right, y: lane },
      { x: left, y: lane },
      { x: left, y: p3.y },
      p3,
    ];
    return { d: roundedPath(points), points, start: p0 };
  }
  let c1;
  let c2;
  if (shape.kind === "arc") {
    const base = shape.up ? Math.min(p0.y, p3.y) : Math.max(p0.y, p3.y);
    // A cubic's middle sits three quarters of the way to its control points.
    const y = base + ((shape.up ? -1 : 1) * shape.depth) / 0.75;
    [c1, c2] = [
      { x: p0.x, y },
      { x: p3.x, y },
    ];
  } else {
    const reach = Math.min(
      160,
      Math.max(24, 0.45 * (p0.nx ? Math.abs(p3.x - p0.x) : Math.abs(p3.y - p0.y))),
    );
    [c1, c2] = [
      { x: p0.x + p0.nx * reach, y: p0.y + p0.ny * reach },
      { x: p3.x + p3.nx * reach, y: p3.y + p3.ny * reach },
    ];
  }
  return {
    d: `M ${p0.x} ${p0.y} C ${c1.x} ${c1.y} ${c2.x} ${c2.y} ${p3.x} ${p3.y}`,
    points: cubicPoints(p0, c1, c2, p3),
    start: p0,
  };
}

/** Whether segment a–b passes through `rect` (Liang–Barsky clipping). */
function segmentHits(a, b, rect) {
  let [t0, t1] = [0, 1];
  const [dx, dy] = [b.x - a.x, b.y - a.y];
  const sides = [
    [-dx, a.x - rect.x],
    [dx, rect.x + rect.w - a.x],
    [-dy, a.y - rect.y],
    [dy, rect.y + rect.h - a.y],
  ];
  for (const [p, q] of sides) {
    if (p === 0) {
      if (q < 0) return false;
      continue;
    }
    const t = q / p;
    if (p < 0) t0 = Math.max(t0, t);
    else t1 = Math.min(t1, t);
    if (t0 > t1) return false;
  }
  return true;
}

function leastCovering(candidates, rects) {
  const covered = (a) =>
    rects.reduce(
      (sum, b) =>
        sum +
        Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) *
          Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y)),
      0,
    );
  return candidates.reduce((best, c) => (covered(c) < covered(best) ? c : best));
}

function pointAlong(points, fraction) {
  const lengths = [0];
  for (let k = 1; k < points.length; k++)
    lengths.push(
      lengths[k - 1] + Math.hypot(points[k].x - points[k - 1].x, points[k].y - points[k - 1].y),
    );
  const goal = lengths.at(-1) * fraction;
  const k = Math.max(
    1,
    lengths.findIndex((l) => l >= goal),
  );
  const t = (goal - lengths[k - 1]) / (lengths[k] - lengths[k - 1] || 1);
  return {
    x: points[k - 1].x + (points[k].x - points[k - 1].x) * t,
    y: points[k - 1].y + (points[k].y - points[k - 1].y) * t,
  };
}

/**
 * Draws a level as its boxes stand. `rects` maps id → { x, y, w, h }; `edges` are the parsed
 * arrows and `hints` how layout.js meant each to run (by index); `noteLinks` join notes to boxes;
 * `labelSize(edge)` → { width, height }; `labelled(i)` says whether arrow i shows its label.
 * Returns { arrows: [{ d, label: { x, y, w, h } | null }], links: [{ d }], bounds }.
 */
export function routeLevel({ rects, edges, noteLinks, hints, labelSize, labelled }) {
  const lines = [
    ...edges.map((e, i) => ({
      ids: [e.from, e.to],
      shape: shapeOf(rects.get(e.from), rects.get(e.to), hints.get(i)),
      ports: [],
    })),
    ...noteLinks.map((l) => ({
      ids: [l.from, l.to],
      shape: { kind: "curve", sides: facing(rects.get(l.from), rects.get(l.to)) },
      ports: [],
    })),
  ];
  assignPorts(lines, rects);
  const drawn = lines.map((line) => draw(line, rects));

  const boxes = [...rects.values()];
  const middle =
    (Math.min(...boxes.map((b) => b.x)) + Math.max(...boxes.map((b) => b.x + b.w))) / 2;
  const taken = [];
  const labels = new Map();
  const order = edges
    .map((_, i) => i)
    .filter((i) => edges[i].label && labelled(i))
    .sort((a, b) => (edges[a].step ?? Infinity) - (edges[b].step ?? Infinity) || a - b);
  // A label goes where it covers no box, no other label and, if it can, no other arrow (its twin
  // between the same two boxes aside).
  const pair = (k) => [...lines[k].ids].sort().join(">");
  const crosses = (rect, j) =>
    drawn.some(
      (other, k) =>
        pair(k) !== pair(j) &&
        other.points.some((p, n) => n > 0 && segmentHits(other.points[n - 1], p, rect)),
    );
  for (const i of order) {
    const { width: w, height: h } = labelSize(edges[i]);
    // Of two arrows side by side, each label leans to its own side, leaving the middle free; a
    // vertical pair stacks its labels on the side facing the drawing, so neither juts out of it.
    const { off, nx } = drawn[i].start;
    const pairX = (cx(rects.get(edges[i].from)) + cx(rects.get(edges[i].to))) / 2;
    const lean = Math.sign(off);
    let offsets = [
      [0, 0],
      [0, -h / 2 - 4],
      [0, h / 2 + 4],
      [w / 2 + 4, 0],
      [-w / 2 - 4, 0],
    ];
    if (lean && nx)
      offsets = [
        [0, lean * (h / 2 + 4)],
        [0, 0],
        [0, -lean * (h / 2 + 4)],
      ];
    else if (lean) {
      const inward = pairX > middle ? -1 : 1;
      offsets = [
        [inward * (w / 2 + 4), lean * (h / 2 + 3)],
        [inward * (w / 2 + 4), 0],
        [0, 0],
        [-inward * (w / 2 + 4), 0],
      ];
    }
    const candidates = ALONG.flatMap((fraction) => {
      const p = pointAlong(drawn[i].points, fraction);
      return offsets.map(([dx, dy]) => ({ x: p.x - w / 2 + dx, y: p.y - h / 2 + dy, w, h }));
    });
    const free = (rect) =>
      !boxes.some((b) => overlaps(rect, b, 4)) && !taken.some((t) => overlaps(rect, t, 3));
    let spot = candidates.find((rect) => free(rect) && !crosses(rect, i)) ?? candidates.find(free);
    if (!spot && edges[i].step !== null) spot = leastCovering(candidates, [...boxes, ...taken]);
    if (spot) {
      taken.push(spot);
      labels.set(i, spot);
    }
  }

  let bounds = null;
  const grow = (x0, y0, x1, y1) => {
    bounds = bounds
      ? {
          x0: Math.min(bounds.x0, x0),
          y0: Math.min(bounds.y0, y0),
          x1: Math.max(bounds.x1, x1),
          y1: Math.max(bounds.y1, y1),
        }
      : { x0, y0, x1, y1 };
  };
  for (const r of [...boxes, ...taken]) grow(r.x, r.y, r.x + r.w, r.y + r.h);
  for (const { points } of drawn) for (const p of points) grow(p.x, p.y, p.x, p.y);
  return {
    arrows: edges.map((_, i) => ({ d: drawn[i].d, label: labels.get(i) ?? null })),
    links: noteLinks.map((_, k) => ({ d: drawn[edges.length + k].d })),
    bounds,
  };
}
