/*
 * The lane grid the router searches: what is free, what earlier arrows hold, and the search itself.
 * Nodes sit every `pitch` px on both axes, at absolute multiples of the pitch, so a route does not
 * shift when the drawing's extent changes. A node is free when it lies in no box's inflated
 * rectangle, no frame title and no earlier label; a horizontal move is also refused within
 * FRAME_CLEAR of a frame's horizontal border and a vertical one within FRAME_CLEAR of a vertical
 * border, so an arrow crosses a border squarely and never runs along it. An arrow's own end boxes
 * are the exception: the strip straight out from a side is open, for the stub only. Every node an
 * arrow passes or bends at is then held, so a later arrow neither shares its lane nor bends on it
 * (it may cross it). Because the search can only step on free nodes, any path it returns keeps the
 * clearances; nothing is repaired afterwards. No DOM.
 */

export const CLEAR = 12;
export const FRAME_CLEAR = 8;
/** An arrow's port may sit anywhere on a side but this far from its corners. */
export const PORT_MARGIN = 10;

const BEND = 40;
const CROSS = 14;
const CROSS_STEP = 34;
const CROSS_FRAME = 40;
const ADJACENT = 5;
const OFF_CENTRE = 0.3;
const LANES_BEYOND = 14;
const MAX_NODES = 150000;

const R = 0;
const D = 1;
const L = 2;
const U = 3;
const DX = [1, 0, -1, 0];
const DY = [0, 1, 0, -1];
const SIDE_DIR = [U, R, D, L]; // top, right, bottom, left: the way out of a box
/** Which way an arrow may move: 1 horizontally, 2 vertically. */
const axisOf = (dir) => (dir & 1 ? 2 : 1);
const BEND_BITS = 7;

const inflate = (r, c) => ({ x: r.x - c, y: r.y - c, w: r.w + 2 * c, h: r.h + 2 * c });

/**
 * `boxes` [{ id, x, y, w, h }], `titles` rectangles to keep clear, `outlines` the frame borders,
 * `frames` the rectangles of whole (not broken) frames.
 */
export function createGrid({ boxes, titles, outlines, frames }) {
  const rects = [...boxes, ...titles, ...outlines];
  let x0 = Math.min(...rects.map((r) => r.x));
  let y0 = Math.min(...rects.map((r) => r.y));
  let x1 = Math.max(...rects.map((r) => r.x + r.w));
  let y1 = Math.max(...rects.map((r) => r.y + r.h));
  let pitch = 8;
  const size = () => {
    const m = LANES_BEYOND * pitch;
    return [Math.ceil((x1 - x0 + 2 * m) / pitch) + 2, Math.ceil((y1 - y0 + 2 * m) / pitch) + 2];
  };
  while (size()[0] * size()[1] > MAX_NODES && pitch < 16) pitch += 2;
  const [nx, ny] = size();
  const ox = Math.floor((x0 - LANES_BEYOND * pitch) / pitch) * pitch;
  const oy = Math.floor((y0 - LANES_BEYOND * pitch) / pitch) * pitch;
  const total = nx * ny;
  const px = (i) => ox + i * pitch;
  const py = (j) => oy + j * pitch;
  const ci = (x) => (x - ox) / pitch;
  const cj = (y) => (y - oy) / pitch;

  // What is there before any arrow is routed.
  const cover = new Uint8Array(total);
  const band = new Uint8Array(total); // 1: no horizontal move, 2: no vertical move
  const prox = new Uint8Array(total);
  const frameAt = new Uint8Array(total);
  // What the arrows routed so far hold.
  const occ = new Uint8Array(total); // bit 1 horizontal, 2 vertical, 4 bend
  const mainOcc = new Uint8Array(total);
  const labelHeld = new Uint8Array(total);
  // What the arrow being routed may do in its end boxes' strips.
  const exSub = new Uint8Array(total);
  const exAxis = new Uint8Array(total).fill(3);
  const exBlock = new Uint8Array(total);
  let touched = [];

  /** Calls fn(i, j) for the nodes in `r`: strictly inside when `strict`, else on or inside. */
  const each = (r, strict, fn) => {
    const span = (lo, hi, origin, n) => {
      const a = (lo - origin) / pitch;
      const b = (hi - origin) / pitch;
      return [Math.max(0, strict ? Math.floor(a) + 1 : Math.ceil(a)), Math.min(n - 1, strict ? Math.ceil(b) - 1 : Math.floor(b))];
    };
    const [i0, i1] = span(r.x, r.x + r.w, ox, nx);
    const [j0, j1] = span(r.y, r.y + r.h, oy, ny);
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) fn(i, j, j * nx + i);
  };

  for (const box of boxes) {
    const zone = inflate(box, CLEAR);
    each(zone, true, (_i, _j, n) => cover[n]++);
    each(inflate(zone, 3 * pitch), true, (i, j, n) => {
      const dx = Math.max(zone.x - px(i), px(i) - (zone.x + zone.w), 0);
      const dy = Math.max(zone.y - py(j), py(j) - (zone.y + zone.h), 0);
      const away = Math.floor(Math.max(dx, dy) / pitch);
      if (away < 3 && dx + dy > 0) prox[n] = Math.min(255, prox[n] + (3 - away) * 2);
    });
  }
  for (const title of titles) each(inflate(title, FRAME_CLEAR), true, (_i, _j, n) => cover[n]++);
  for (const o of outlines) {
    each({ x: o.x, y: o.y - FRAME_CLEAR, w: o.w, h: 2 * FRAME_CLEAR }, true, (_i, _j, n) => (band[n] |= 1));
    each({ x: o.x, y: o.y + o.h - FRAME_CLEAR, w: o.w, h: 2 * FRAME_CLEAR }, true, (_i, _j, n) => (band[n] |= 1));
    each({ x: o.x - FRAME_CLEAR, y: o.y, w: 2 * FRAME_CLEAR, h: o.h }, true, (_i, _j, n) => (band[n] |= 2));
    each({ x: o.x + o.w - FRAME_CLEAR, y: o.y, w: 2 * FRAME_CLEAR, h: o.h }, true, (_i, _j, n) => (band[n] |= 2));
  }
  frames.forEach((f, k) => each(f, false, (_i, _j, n) => (frameAt[n] = k + 1)));

  const passable = (n, axis) =>
    cover[n] <= exSub[n] &&
    !exBlock[n] &&
    (exAxis[n] & axis) !== 0 &&
    !labelHeld[n] &&
    !(band[n] & axis) &&
    !(occ[n] & (axis | 4));

  /** Opens the strips straight out of each side of `ends` for the arrow about to be routed. */
  function begin(ends) {
    for (const box of ends) {
      each(inflate(box, CLEAR), true, (i, j, n) => {
        const x = px(i);
        const y = py(j);
        const along = (lo, hi, v) => v >= lo + PORT_MARGIN && v <= hi - PORT_MARGIN;
        let axis = 0;
        if (along(box.x, box.x + box.w, x) && y < box.y) axis = 2;
        else if (along(box.x, box.x + box.w, x) && y > box.y + box.h) axis = 2;
        else if (along(box.y, box.y + box.h, y) && x < box.x) axis = 1;
        else if (along(box.y, box.y + box.h, y) && x > box.x + box.w) axis = 1;
        touched.push(n);
        if (axis) {
          exSub[n]++;
          exAxis[n] &= axis;
        } else exBlock[n] = 1;
      });
    }
  }

  function end() {
    for (const n of touched) {
      exSub[n] = 0;
      exAxis[n] = 3;
      exBlock[n] = 0;
    }
    touched = [];
  }

  /**
   * Where an arrow may leave or enter `box`: { state, g, x, y, side, dir } per lane of each side whose
   * first node out is free. `state` is that node with the way out; g its cost to start there.
   */
  function ports(box, others) {
    const out = [];
    const zones = others.map((o) => inflate(o, CLEAR));
    for (let side = 0; side < 4; side++) {
      const dir = SIDE_DIR[side];
      const across = side === 0 || side === 2;
      const lo = across ? box.x : box.y;
      const hi = across ? box.x + box.w : box.y + box.h;
      const centre = (lo + hi) / 2;
      const edge = [box.y, box.x + box.w, box.y + box.h, box.x][side];
      const first = across
        ? Math.ceil(ci(lo + PORT_MARGIN))
        : Math.ceil(cj(lo + PORT_MARGIN));
      const last = across ? Math.floor(ci(hi - PORT_MARGIN)) : Math.floor(cj(hi - PORT_MARGIN));
      for (let k = first; k <= last; k++) {
        const along = across ? px(k) : py(k);
        const point = across ? { x: along, y: edge } : { x: edge, y: along };
        if (zones.some((z) => point.x > z.x && point.x < z.x + z.w && point.y > z.y && point.y < z.y + z.h)) continue;
        // The first node out: the nearest line beyond the side.
        let i;
        let j;
        if (side === 0) [i, j] = [k, Math.ceil(cj(edge)) - 1];
        else if (side === 2) [i, j] = [k, Math.floor(cj(edge)) + 1];
        else if (side === 1) [i, j] = [Math.floor(ci(edge)) + 1, k];
        else [i, j] = [Math.ceil(ci(edge)) - 1, k];
        if (i < 0 || j < 0 || i >= nx || j >= ny) continue;
        const n = j * nx + i;
        if (!passable(n, axisOf(dir))) continue;
        const stub = Math.abs(px(i) - point.x) + Math.abs(py(j) - point.y);
        out.push({
          state: n * 4 + dir,
          g: stub + Math.abs(along - centre) * OFF_CENTRE,
          x: point.x,
          y: point.y,
          side,
          dir,
        });
      }
    }
    return out;
  }

  // ---- The search ----

  const best = new Float32Array(total * 4);
  const seen = new Uint32Array(total * 4);
  const closed = new Uint32Array(total * 4);
  const from = new Int32Array(total * 4);
  let round = 0;
  let heapF = [];
  let heapS = [];

  function push(f, s) {
    let k = heapF.length;
    heapF.push(f);
    heapS.push(s);
    while (k > 0) {
      const up = (k - 1) >> 1;
      if (heapF[up] <= f) break;
      heapF[k] = heapF[up];
      heapS[k] = heapS[up];
      k = up;
    }
    heapF[k] = f;
    heapS[k] = s;
  }

  function pop() {
    const s = heapS[0];
    const f = heapF.pop();
    const t = heapS.pop();
    const n = heapF.length;
    if (n) {
      let k = 0;
      for (;;) {
        let c = 2 * k + 1;
        if (c >= n) break;
        if (c + 1 < n && heapF[c + 1] < heapF[c]) c++;
        if (heapF[c] >= f) break;
        heapF[k] = heapF[c];
        heapS[k] = heapS[c];
        k = c;
      }
      heapF[k] = f;
      heapS[k] = t;
    }
    return s;
  }

  /**
   * The cheapest way from `starts` [{ state, g }] to a state of `goals` (state → { extra }): the list
   * of states, each a node and the way it was entered, or null. Costs are length, bends, crossing
   * other arrows, crossing frame borders and nearness to boxes.
   */
  function search(starts, goals) {
    if (!starts.length || !goals.size) return null;
    round++;
    heapF = [];
    heapS = [];
    let gi0 = Infinity;
    let gi1 = -Infinity;
    let gj0 = Infinity;
    let gj1 = -Infinity;
    for (const state of goals.keys()) {
      const n = state >> 2;
      const i = n % nx;
      const j = (n / nx) | 0;
      gi0 = Math.min(gi0, i);
      gi1 = Math.max(gi1, i);
      gj0 = Math.min(gj0, j);
      gj1 = Math.max(gj1, j);
    }
    const h = (n) => {
      const i = n % nx;
      const j = (n / nx) | 0;
      return pitch * (Math.max(0, gi0 - i, i - gi1) + Math.max(0, gj0 - j, j - gj1));
    };
    const relax = (state, g, parent) => {
      if (seen[state] === round && best[state] <= g) return;
      seen[state] = round;
      best[state] = g;
      from[state] = parent;
      push(g + h(state >> 2), state);
    };
    for (const s of starts) relax(s.state, s.g, -1);
    while (heapF.length) {
      const state = pop();
      if (state < 0) return trace(~state);
      if (closed[state] === round) continue;
      closed[state] = round;
      const goal = goals.get(state);
      if (goal) {
        // A port's own cost is paid before it ends the search, so a dearer port waits its turn.
        if (!goal.extra) return trace(state);
        push(best[state] + goal.extra, ~state);
      }
      const n = state >> 2;
      const d = state & 3;
      const g = best[state];
      const i = n % nx;
      const j = (n / nx) | 0;
      const i2 = i + DX[d];
      const j2 = j + DY[d];
      if (i2 >= 0 && j2 >= 0 && i2 < nx && j2 < ny) {
        const n2 = j2 * nx + i2;
        const axis = axisOf(d);
        if (passable(n2, axis)) {
          let cost = pitch + prox[n2];
          if (occ[n2] & (3 - axis)) cost += mainOcc[n2] ? CROSS_STEP : CROSS;
          if (axis === 1 ? (j > 0 && occ[n2 - nx] & 1) || (j < ny - 1 && occ[n2 + nx] & 1) : (i > 0 && occ[n2 - 1] & 2) || (i < nx - 1 && occ[n2 + 1] & 2)) cost += ADJACENT;
          if (frameAt[n2] !== frameAt[n]) cost += CROSS_FRAME;
          relax(n2 * 4 + d, g + cost, state);
        }
      }
      if (passable(n, 1) && passable(n, 2)) {
        relax(n * 4 + ((d + 1) & 3), g + BEND, state);
        relax(n * 4 + ((d + 3) & 3), g + BEND, state);
      }
    }
    return null;
  }

  function trace(state) {
    const states = [];
    for (let s = state; s !== -1; s = from[s]) states.push(s);
    return states.reverse();
  }

  // ---- What a finished arrow holds ----

  /** Holds the nodes of `states`; returns the undo list. */
  function hold(states, main, undo = []) {
    states.forEach((state, k) => {
      const n = state >> 2;
      const turns = states[k + 1] >> 2 === n || states[k - 1] >> 2 === n;
      undo.push(n, occ[n], mainOcc[n]);
      occ[n] |= turns ? BEND_BITS : axisOf(state & 3);
      if (main) mainOcc[n] = 1;
    });
    return undo;
  }

  /** Keeps later arrows out of `r` (a label); returns the undo list. */
  function holdRect(r, undo = []) {
    each(inflate(r, 5), true, (_i, _j, n) => {
      undo.push(~n, labelHeld[n], 0);
      labelHeld[n] = 1;
    });
    return undo;
  }

  function release(undo) {
    for (let k = undo.length - 3; k >= 0; k -= 3) {
      if (undo[k] < 0) labelHeld[~undo[k]] = undo[k + 1];
      else {
        occ[undo[k]] = undo[k + 1];
        mainOcc[undo[k]] = undo[k + 2];
      }
    }
  }

  const point = (state) => ({ x: px((state >> 2) % nx), y: py(((state >> 2) / nx) | 0) });
  const stateAt = (x, y, dir) => (Math.round(cj(y)) * nx + Math.round(ci(x))) * 4 + dir;
  const free = (x, y, axis) => {
    const i = Math.round(ci(x));
    const j = Math.round(cj(y));
    return i >= 0 && j >= 0 && i < nx && j < ny && passable(j * nx + i, axis);
  };

  return {
    pitch,
    bounds: { x0: px(0), y0: py(0), x1: px(nx - 1), y1: py(ny - 1) },
    begin,
    end,
    ports,
    search,
    hold,
    holdRect,
    release,
    point,
    stateAt,
    free,
  };
}

export { D, R };
