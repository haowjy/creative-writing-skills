/*
 * Where a level's boxes go, from their measured sizes, so a page carries no coordinates. The
 * numbered path is the spine: its boxes sit on one row in step order, left to right, and the row
 * wraps like a line of text only when it can't be drawn readably in one. Every other box, and every
 * note, sits in a band above or below the row, near what it connects to. No DOM: map.js measures.
 */

/** Card text is 15px and 12px (page.css): at this zoom it is 13.8px and 11px on screen. */
export const READABLE_ZOOM = 0.92;

const MIN_ROW_GAP = 72;
const LABEL_MARGIN = 10;
const BAND_GAP = 64;
const OUTER_BAND_GAP = 48;
const BOX_GAP = 28;
const MIN_BLOCK_GAP = 84;
const ARC_FIRST = 38;
const ARC_STEP = 60;
const FIT_PAD = 16;

/**
 * The spine and the spurs of the numbered path. A step's box joins the row when it follows the
 * row's last box and the path goes on from it (or nothing else does). A spur sits beside the box
 * it came from: a box the path visits without going on, or whose next step comes straight back (a
 * round trip to the server, say). A box that first appears as the start of a step into a placed
 * box is a spur beside that box.
 */
function mainPath(edges) {
  const steps = edges.filter((e) => e.step !== null).sort((a, b) => a.step - b.step);
  const spine = [];
  const spurOf = new Map();
  const placed = (id) => spine.includes(id) || spurOf.has(id);
  steps.forEach((s, k) => {
    const later = steps.slice(k + 1);
    if (!placed(s.from)) {
      if (placed(s.to)) spurOf.set(s.from, s.to);
      else spine.push(s.from);
    }
    if (placed(s.to)) return;
    const goesOn = later.some((l) => l.from === s.to);
    const fromGoesOn = later.some((l) => l.from === s.from);
    const roundTrip = later[0]?.from === s.to && later[0]?.to === s.from;
    if (s.from === spine.at(-1) && !roundTrip && (goesOn || !fromGoesOn)) spine.push(s.to);
    else spurOf.set(s.to, s.from);
  });
  return { spine, spurOf };
}

/**
 * Left edges for one band's boxes ({ id, want: centre x, w, weight }), each as near its wish as the
 * others allow; a heavier box moves less.
 */
function pack(items) {
  const clusters = [];
  for (const item of [...items].sort((a, b) => a.want - b.want)) {
    clusters.push({
      items: [item],
      width: item.w,
      sum: (item.want - item.w / 2) * item.weight,
      n: item.weight,
    });
    while (clusters.length > 1) {
      const [before, last] = clusters.slice(-2);
      if (before.sum / before.n + before.width + BOX_GAP <= last.sum / last.n) break;
      // Merged, the cluster's left edge is where its members' weighted wishes balance.
      const offset = before.width + BOX_GAP;
      before.sum += last.sum - offset * last.n;
      before.n += last.n;
      before.width = offset + last.width;
      before.items.push(...last.items);
      clusters.pop();
    }
  }
  const left = new Map();
  for (const c of clusters) {
    let x = c.sum / c.n;
    for (const item of c.items) {
      left.set(item.id, x);
      x += item.w + BOX_GAP;
    }
  }
  return left;
}

/**
 * Places the boxes with the spine wrapped at `perRow` boxes. Returns { positions, hints, bounds }:
 * top-left positions by id, and per arrow index how it is drawn ({ kind: "row" | "arc" | "wrap" }).
 */
function arrange(perRow, { spine, spurOf }, { nodes, edges, noteLinks, sizes, labelSize }) {
  const size = (id) => sizes.get(id) ?? { width: 180, height: 64 };
  const rows = [];
  for (let i = 0; i < spine.length; i += perRow) rows.push(spine.slice(i, i + perRow));
  const rowOf = new Map();
  const indexOf = new Map();
  rows.forEach((row, r) => {
    row.forEach((id, i) => {
      rowOf.set(id, r);
      indexOf.set(id, i);
    });
  });
  const between = (a, b) =>
    edges.filter((e) => (e.from === a && e.to === b) || (e.from === b && e.to === a));

  // The spine's centres along each row: a gap holds the widest label of the arrows across it.
  const cx = new Map();
  const rowRight = [];
  rows.forEach((row) => {
    let x = 0;
    row.forEach((id, i) => {
      if (i > 0) {
        const widest = Math.max(0, ...between(row[i - 1], id).map((e) => labelSize(e).width));
        x += Math.max(MIN_ROW_GAP, widest + 2 * LABEL_MARGIN);
      }
      cx.set(id, x + size(id).width / 2);
      x += size(id).width;
    });
    rowRight.push(x);
  });

  // Arrows along a row: neighbours join straight, others arc over (forward) or under (back),
  // nested arcs one level deeper so their labels clear each other.
  const hints = new Map();
  const reach = rows.map(() => ({ above: 0, below: 0 }));
  const arcs = [];
  edges.forEach((e, i) => {
    if (!rowOf.has(e.from) || !rowOf.has(e.to)) return;
    const [rf, rt] = [rowOf.get(e.from), rowOf.get(e.to)];
    if (rf === rt) {
      const [a, b] = [indexOf.get(e.from), indexOf.get(e.to)];
      if (Math.abs(a - b) === 1) hints.set(i, { kind: "row" });
      else
        arcs.push({
          i,
          r: rf,
          side: b > a ? "above" : "below",
          lo: Math.min(a, b),
          hi: Math.max(a, b),
        });
    } else if (
      rt === rf + 1 &&
      indexOf.get(e.from) === rows[rf].length - 1 &&
      indexOf.get(e.to) === 0
    ) {
      hints.set(i, { kind: "wrap", lane: 0, row: rf });
    }
  });
  arcs.sort((a, b) => a.hi - a.lo - (b.hi - b.lo));
  arcs.forEach((arc, k) => {
    const under = arcs
      .slice(0, k)
      .filter(
        (o) =>
          o.r === arc.r && o.side === arc.side && Math.max(o.lo, arc.lo) < Math.min(o.hi, arc.hi),
      );
    arc.level = 1 + Math.max(0, ...under.map((o) => o.level));
    const depth = ARC_FIRST + (arc.level - 1) * ARC_STEP;
    hints.set(arc.i, { kind: "arc", side: arc.side, depth });
    reach[arc.r][arc.side] = Math.max(
      reach[arc.r][arc.side],
      depth + labelSize(edges[arc.i]).height / 2,
    );
  });

  // Every other box gets a row, a side, a band (1 is next to the row) and the x it would like.
  const band = new Map();
  const want = (id) => (rowOf.has(id) ? cx.get(id) : band.get(id).want);
  const chooseSide = (r, x, w) => {
    // A spur's arrows crowd the space beside it, so it counts double.
    const near = (side) =>
      [...band]
        .filter(
          ([, b]) =>
            b.r === r &&
            b.side === side &&
            b.depth === 1 &&
            Math.abs(b.want - x) < (b.w + w) / 2 + BOX_GAP,
        )
        .reduce((n, [id]) => n + (spurOf.has(id) ? 2 : 1), 0);
    const count = (side) => [...band.values()].filter((b) => b.r === r && b.side === side).length;
    const [a, b] = [near("above"), near("below")];
    if (a !== b) return a < b ? "above" : "below";
    return count("below") < count("above") ? "below" : "above";
  };
  const spursOn = new Map();
  for (const [id, anchor] of spurOf) {
    const from = rowOf.has(anchor) ? { r: rowOf.get(anchor), depth: 0 } : band.get(anchor);
    const n = spursOn.get(anchor) ?? 0;
    spursOn.set(anchor, n + 1);
    const side = from.depth === 0 ? (n % 2 === 0 ? "above" : "below") : from.side;
    band.set(id, { r: from.r, side, depth: from.depth + 1, want: want(anchor), w: size(id).width });
  }
  const boxes = nodes.filter((n) => n.kind !== "note").map((n) => n.id);
  const neighbours = new Map(boxes.map((id) => [id, []]));
  for (const e of edges) {
    neighbours.get(e.from)?.push(e.to);
    neighbours.get(e.to)?.push(e.from);
  }
  const queue = [...spine, ...spurOf.keys()];
  const placed = (id) => rowOf.has(id) || band.has(id);
  const visit = () => {
    while (queue.length) {
      const id = queue.shift();
      for (const next of neighbours.get(id) ?? []) {
        if (placed(next)) continue;
        const known = neighbours.get(next).filter(placed);
        const x = known.reduce((sum, k) => sum + want(k), 0) / known.length;
        const anchor = rowOf.has(id) ? { r: rowOf.get(id), depth: 0 } : band.get(id);
        const side = anchor.depth === 0 ? chooseSide(anchor.r, x, size(next).width) : anchor.side;
        band.set(next, {
          r: anchor.r,
          side,
          depth: anchor.depth + 1,
          want: x,
          w: size(next).width,
        });
        queue.push(next);
      }
    }
  };
  visit();
  // Boxes the arrows don't reach (tools beside the system, a separate pair) go wherever the last
  // row's bands have room, beside a box they share a note with.
  const noted = (id) =>
    noteLinks
      .filter((l) => l.from === id || l.to === id)
      .map((l) => (l.from === id ? l.to : l.from));
  for (const id of boxes) {
    if (placed(id)) continue;
    const w = size(id).width;
    const partner = noted(id)
      .flatMap((note) => noted(note))
      .find((other) => band.has(other));
    const r = partner ? band.get(partner).r : rows.length - 1;
    const x = partner
      ? band.get(partner).want + (band.get(partner).w + w) / 2 + BOX_GAP
      : rowRight[r] / 2;
    const side = partner ? band.get(partner).side : chooseSide(r, x, w);
    band.set(id, { r, side, depth: partner ? band.get(partner).depth : 1, want: x, w });
    queue.push(id);
    visit();
  }
  for (const note of nodes.filter((n) => n.kind === "note")) {
    const linked = noteLinks
      .flatMap((l) => (l.from === note.id ? [l.to] : l.to === note.id ? [l.from] : []))
      .filter(placed);
    if (!linked.length) continue;
    const inBand = linked.map((id) => band.get(id)).filter(Boolean);
    const x = linked.reduce((sum, id) => sum + want(id), 0) / linked.length;
    const r = rowOf.get(linked[0]) ?? band.get(linked[0]).r;
    const w = size(note.id).width;
    const side = inBand[0]?.side ?? chooseSide(r, x, w);
    const depth = 1 + Math.max(0, ...inBand.filter((b) => b.side === side).map((b) => b.depth));
    band.set(note.id, { r, side, depth, want: x, w });
  }

  // Horizontal: pack each band. Vertical: bands stack out from their row; rows stack down the page.
  const x = new Map();
  for (const id of spine) x.set(id, cx.get(id) - size(id).width / 2);
  const bands = new Map();
  for (const [id, b] of band) {
    const key = `${b.r}:${b.side}:${b.depth}`;
    if (!bands.has(key)) bands.set(key, []);
    // A spur stays over the box it leaves from; the others make room.
    bands.get(key).push({ id, want: b.want, w: b.w, weight: spurOf.has(id) ? 10 : 1 });
  }
  for (const [key, items] of bands) {
    const left = pack(items);
    // A band that fits within its row's width stays within it, so the drawing is no wider than the row.
    const r = Number(key.split(":")[0]);
    const lo = Math.min(...left.values());
    const hi = Math.max(...items.map((it) => left.get(it.id) + it.w));
    const shift =
      hi > rowRight[r]
        ? -Math.min(hi - rowRight[r], Math.max(0, lo))
        : lo < 0
          ? Math.min(-lo, Math.max(0, rowRight[r] - hi))
          : 0;
    for (const [id, l] of left) x.set(id, l + shift);
  }

  const y = new Map();
  const blocks = rows.map((row, r) => {
    const rowH = Math.max(...row.map((id) => size(id).height));
    for (const id of row) y.set(id, -size(id).height / 2);
    let top = -rowH / 2 - reach[r].above;
    let bottom = rowH / 2 + reach[r].below;
    for (const side of ["above", "below"]) {
      let edge = side === "above" ? -rowH / 2 : rowH / 2;
      for (let depth = 1; ; depth++) {
        const members = [...band]
          .filter(([, b]) => b.r === r && b.side === side && b.depth === depth)
          .map(([id]) => id);
        if (!members.length) break;
        // A numbered arrow across the gap shows its label there, so the gap holds it.
        const inner = (id) =>
          depth === 1
            ? rowOf.get(id) === r
            : band.get(id)?.r === r &&
              band.get(id).side === side &&
              band.get(id).depth === depth - 1;
        const crossing = edges.filter(
          (e) =>
            e.step !== null &&
            ((members.includes(e.from) && inner(e.to)) ||
              (members.includes(e.to) && inner(e.from))),
        );
        const stacked = new Map();
        for (const e of crossing) {
          const pair = [e.from, e.to].sort().join(">");
          stacked.set(pair, (stacked.get(pair) ?? 16) + labelSize(e).height + 8);
        }
        const label = Math.max(0, ...stacked.values());
        const gap = Math.max(
          depth === 1 ? Math.max(BAND_GAP, reach[r][side] + 24) : OUTER_BAND_GAP,
          label,
        );
        const h = Math.max(...members.map((id) => size(id).height));
        for (const id of members)
          y.set(id, side === "above" ? edge - gap - size(id).height : edge + gap);
        edge = side === "above" ? edge - gap - h : edge + gap + h;
      }
      if (side === "above") top = Math.min(top, edge);
      else bottom = Math.max(bottom, edge);
    }
    return { top, bottom };
  });
  const shift = [];
  let cursor = 0;
  blocks.forEach((b, r) => {
    if (r > 0) {
      const wraps = [...hints].filter(([, h]) => h.kind === "wrap" && h.row === r - 1);
      const gap = Math.max(MIN_BLOCK_GAP, ...wraps.map(([i]) => labelSize(edges[i]).height + 40));
      for (const [, h] of wraps) h.lane = cursor + gap / 2;
      cursor += gap;
    }
    shift.push(cursor - b.top);
    cursor += b.bottom - b.top;
  });
  const positions = new Map();
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
  for (const id of nodes.map((n) => n.id)) {
    if (!x.has(id)) continue;
    const r = rowOf.get(id) ?? band.get(id).r;
    const p = { x: x.get(id), y: y.get(id) + shift[r] };
    positions.set(id, p);
    grow(p.x, p.y, p.x + size(id).width, p.y + size(id).height);
  }
  blocks.forEach((b, r) => {
    grow(bounds.x0, b.top + shift[r], bounds.x1, b.bottom + shift[r]);
  });
  return { positions, hints, bounds };
}

/** The zoom that fits `bounds` in `area`, leaving a margin. */
export function fitZoom(bounds, area) {
  return Math.min(
    (area.width - 2 * FIT_PAD) / (bounds.x1 - bounds.x0),
    (area.height - 2 * FIT_PAD) / (bounds.y1 - bounds.y0),
  );
}

/**
 * The layout of a level for a drawing `area` ({ width, height }): the longest row that still fits
 * readably, else the arrangement that draws largest. `nodes` are { id, kind }, `edges` the parsed
 * arrows, `noteLinks` { from, to }, `sizes` id → { width, height }, `labelSize(edge)` → { width, height }.
 * Returns { positions: Map id → { x, y }, hints: Map arrow index → hint }.
 */
export function layoutLevel(level, area) {
  const path = mainPath(level.edges);
  if (!path.spine.length) path.spine.push(level.nodes.find((n) => n.kind !== "note").id);
  let best = null;
  for (let perRow = path.spine.length; perRow >= 1; perRow--) {
    const layout = arrange(perRow, path, level);
    layout.zoom = fitZoom(layout.bounds, area);
    if (layout.zoom >= READABLE_ZOOM) return layout;
    if (!best || layout.zoom > best.zoom) best = layout;
  }
  return best;
}
