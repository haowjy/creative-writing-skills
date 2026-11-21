/*
 * Where a level's boxes go, from their measured sizes, so a page carries no coordinates. The
 * numbered path is the spine. Frames are placement blocks: their members stay together in a
 * sensible grid whose gaps make room for the arrows and labels between them, while branch units and
 * outside services sit beside the unit they connect to.
 * The spine wraps before it becomes wider than a readable view. No DOM: map.js measures.
 */

import { frameOutline, GROUP_BOTTOM, GROUP_SIDE, GROUP_TOP } from "./frames.js";

/** Card text is 15px and 12px (page.css): at this zoom it remains readable on screen. */
export const READABLE_ZOOM = 0.78;

const ROW_GAP = 92;
const UNIT_GAP = 46;
const BOX_GAP = 34;
const SIDE_GAP = 28;
const NOTE_GAP = 44;
const FIT_PAD = 10;

/** The numbered path, with a branch box kept beside the spine instead of inserted into it. */
function mainPath(edges) {
  const steps = edges.filter((edge) => edge.step !== null).sort((a, b) => a.step - b.step);
  const spine = [];
  const spurOf = new Map();
  const placed = (id) => spine.includes(id) || spurOf.has(id);
  steps.forEach((step, index) => {
    const previous = steps[index - 1];
    if (!placed(step.from)) {
      if (placed(step.to)) spurOf.set(step.from, step.to);
      else spine.push(step.from);
    }
    if (placed(step.to)) return;
    if (!previous || previous.to === step.from) spine.push(step.to);
    else spurOf.set(step.to, step.from);
  });
  return { spine, spurOf };
}

const frameRect = (frame, positions, sizes) => {
  const members = frame.nodes
    .map((id) => ({ position: positions.get(id), size: sizes.get(id) }))
    .filter((member) => member.position && member.size)
    .map(({ position, size }) => ({ x: position.x, y: position.y, w: size.width, h: size.height }));
  if (!members.length) return null;
  return { ...frameOutline(members), label: frame.label, nodes: frame.nodes };
};

const overlaps = (a, b, gap = 0) =>
  a.x < b.x + b.w + gap && b.x < a.x + a.w + gap && a.y < b.y + b.h + gap && b.y < a.y + a.h + gap;

const rectForUnit = (unit, positions, sizes, frames) => {
  if (unit.frame) return frameRect(frames.get(unit.id), positions, sizes);
  const p = positions.get(unit.id);
  const s = sizes.get(unit.id);
  return p && s ? { x: p.x, y: p.y, w: s.width, h: s.height } : null;
};

/**
 * Build a deterministic frame block and return its member offsets. A grid gap is widened by the
 * arrows that cross it: labels get their full measured width, and parallel arrows get additional
 * clearance instead of being squeezed into one fixed-size gutter.
 */
function blockFor(frame, sizes, edges, labelSize) {
  const members = frame.nodes.map((id) => ({ id, size: sizes.get(id) })).filter((m) => m.size);
  if (!members.length) return null;
  const columns = members.length <= 2 ? members.length : Math.ceil(Math.sqrt(members.length));
  const rows = Math.ceil(members.length / columns);
  const widths = Array.from({ length: columns }, () => 0);
  const heights = Array.from({ length: rows }, () => 0);
  const columnOf = new Map();
  const rowOf = new Map();
  members.forEach((member, index) => {
    const column = index % columns;
    const row = Math.floor(index / columns);
    columnOf.set(member.id, column);
    rowOf.set(member.id, row);
    widths[column] = Math.max(widths[column], member.size.width);
    heights[row] = Math.max(heights[row], member.size.height);
  });
  const horizontal = Array.from({ length: Math.max(0, columns - 1) }, () => BOX_GAP);
  const vertical = Array.from({ length: Math.max(0, rows - 1) }, () => BOX_GAP);
  const horizontalCount = horizontal.map(() => 0);
  const verticalCount = vertical.map(() => 0);
  for (const edge of edges) {
    if (!columnOf.has(edge.from) || !columnOf.has(edge.to)) continue;
    const fromColumn = columnOf.get(edge.from);
    const toColumn = columnOf.get(edge.to);
    const fromRow = rowOf.get(edge.from);
    const toRow = rowOf.get(edge.to);
    const measured = labelSize(edge);
    const loColumn = Math.min(fromColumn, toColumn);
    const hiColumn = Math.max(fromColumn, toColumn);
    for (let column = loColumn; column < hiColumn; column++) {
      horizontalCount[column] += 1;
      horizontal[column] = Math.max(horizontal[column], measured.width + 18);
    }
    const loRow = Math.min(fromRow, toRow);
    const hiRow = Math.max(fromRow, toRow);
    for (let row = loRow; row < hiRow; row++) {
      verticalCount[row] += 1;
      vertical[row] = Math.max(vertical[row], measured.height + 18);
    }
  }
  horizontal.forEach((gap, index) => {
    horizontal[index] = Math.max(gap, gap + Math.max(0, horizontalCount[index] - 1) * 10);
  });
  vertical.forEach((gap, index) => {
    vertical[index] = Math.max(gap, gap + Math.max(0, verticalCount[index] - 1) * 10);
  });
  const offsets = new Map();
  let y = GROUP_TOP;
  for (let row = 0; row < rows; row++) {
    let x = GROUP_SIDE;
    for (let column = 0; column < columns; column++) {
      const index = row * columns + column;
      const member = members[index];
      if (!member) continue;
      offsets.set(member.id, { x, y });
      x += widths[column] + (horizontal[column] ?? 0);
    }
    y += heights[row] + (vertical[row] ?? 0);
  }
  return {
    offsets,
    width: GROUP_SIDE * 2 + widths.reduce((sum, width) => sum + width, 0) + horizontal.reduce((sum, gap) => sum + gap, 0),
    height: GROUP_TOP + GROUP_BOTTOM + heights.reduce((sum, height) => sum + height, 0) + vertical.reduce((sum, gap) => sum + gap, 0),
  };
}

function unitGap(left, right, edges, labelSize) {
  const linked = edges.filter(
    (edge) =>
      (left.nodes.includes(edge.from) && right.nodes.includes(edge.to)) ||
      (left.nodes.includes(edge.to) && right.nodes.includes(edge.from)),
  );
  return Math.max(UNIT_GAP, ...linked.map((edge) => labelSize(edge).width + 18));
}

function arrange(perRow, units, { sizes, frames, area, labelSize }) {
  const positions = new Map();
  const rows = [];
  for (let i = 0; i < units.length; i += perRow) rows.push(units.slice(i, i + perRow));
  let y = 0;
  for (const row of rows) {
    const height = Math.max(...row.map((unit) => unit.height));
    let x = 0;
    for (const [index, unit] of row.entries()) {
      if (unit.frame) {
        for (const [id, offset] of unit.block.offsets)
          positions.set(id, { x: x + offset.x, y: y + offset.y + (height - unit.height) / 2 });
      } else positions.set(unit.id, { x, y: y + (height - unit.height) / 2 });
      if (index < row.length - 1) x += unit.width + unitGap(unit, row[index + 1], units.edges, labelSize);
    }
    y += height + ROW_GAP;
  }

  const placedUnits = [...units];
  const sideUnits = units.allSide ?? [];
  const maxWidth = Math.max(area.width / READABLE_ZOOM, area.width);
  const unitBounds = () => placedUnits.map((unit) => rectForUnit(unit, positions, sizes, frames)).filter(Boolean);
  // Frames that are not on the spine form the next row. This keeps a branch frame beside
  // the spine without stacking every branch underneath the previous one.
  const sideFrames = sideUnits.filter((unit) => unit.frame);
  let sideX = 0;
  let sideY = Math.max(0, ...unitBounds().map((rect) => rect.y + rect.h)) + ROW_GAP;
  let sideRowHeight = 0;
  for (const [index, unit] of sideFrames.entries()) {
    const previous = sideFrames[index - 1];
    const gap = previous ? unitGap(previous, unit, units.edges, labelSize) : 0;
    if (sideX && sideX + gap + unit.width > maxWidth) {
      sideX = 0;
      sideY += sideRowHeight + ROW_GAP;
      sideRowHeight = 0;
    } else if (sideX) sideX += gap;
    for (const [id, offset] of unit.block.offsets)
      positions.set(id, { x: sideX + offset.x, y: sideY + offset.y });
    placedUnits.push(unit);
    sideX += unit.width;
    sideRowHeight = Math.max(sideRowHeight, unit.height);
  }
  if (sideFrames.length) sideY += sideRowHeight + ROW_GAP;
  const placeSide = (unit) => {
    const connected = unit.nodes
      .flatMap((id) => units.edges.filter((edge) => edge.from === id || edge.to === id))
      .map((edge) => (unit.nodes.includes(edge.from) ? edge.to : edge.from))
      .filter((id) => positions.has(id) || units.byNode.has(id));
    const anchorNode = connected.find((id) => positions.has(id));
    const anchorUnit = anchorNode ? units.byNode.get(anchorNode) : null;
    const anchor = anchorUnit ? rectForUnit(anchorUnit, positions, sizes, frames) : null;
    const target = anchorNode
      ? { position: positions.get(anchorNode), size: sizes.get(anchorNode) }
      : null;
    const alignedY = target?.position?.y ?? anchor?.y ?? 0;
    const candidates = [];
    if (anchor) {
      // An outside service connects to the member box, but must clear that member's frame. Keep its
      // y aligned to the member while using the frame edge as the x edge.
      candidates.push(
        { x: anchor.x + anchor.w + SIDE_GAP, y: alignedY },
        { x: anchor.x - unit.width - SIDE_GAP, y: alignedY },
        { x: anchor.x, y: anchor.y + anchor.h + SIDE_GAP },
        { x: anchor.x, y: anchor.y - unit.height - SIDE_GAP },
      );
    }
    candidates.push({ x: 0, y });
    const occupied = () => unitBounds();
    let chosen = null;
    if (anchorUnit?.frame && anchor) {
      const x = Math.min(anchor.x + anchor.w + SIDE_GAP, maxWidth - unit.width);
      let y = Math.max(0, alignedY);
      while (
        occupied().some((other) => overlaps({ x, y, w: unit.width, h: unit.height }, other, 8)) &&
        y < anchor.y + anchor.h + 4 * (unit.height + SIDE_GAP)
      )
        y += unit.height + SIDE_GAP;
      chosen = { x: Math.max(0, x), y };
    }
    if (!chosen)
      chosen = candidates.find(
        (candidate) =>
          candidate.x >= 0 &&
          candidate.y >= 0 &&
          candidate.x + unit.width <= maxWidth &&
          !occupied().some((other) => overlaps({ ...candidate, w: unit.width, h: unit.height }, other, 8)),
      );
    if (!chosen) {
      const rowY = Math.max(y, ...occupied().map((r) => r.y + r.h + ROW_GAP));
      let x = 0;
      while (x + unit.width > maxWidth && x > 0) x = 0;
      chosen = { x, y: rowY };
    }
    if (unit.frame) {
      for (const [id, offset] of unit.block.offsets)
        positions.set(id, { x: chosen.x + offset.x, y: chosen.y + offset.y });
    } else positions.set(unit.id, chosen);
    placedUnits.push(unit);
  };
  for (const unit of sideUnits.filter((candidate) => !candidate.frame)) placeSide(unit);
  // A note sits beside the box it is linked to, wherever there is room, clear of every unit.
  const placedNotes = [];
  for (const note of units.notes) {
    const { width: w, height: h } = note.size;
    const anchor = note.anchors.map((id) => units.byNode.get(id)).find(Boolean);
    const at = anchor ? rectForUnit(anchor, positions, sizes, frames) : { x: 0, y: 0, w: 0, h: 0 };
    const taken = () => [...unitBounds(), ...placedNotes];
    const options = [
      (k) => ({ x: at.x + at.w + NOTE_GAP, y: at.y + k * (h + NOTE_GAP) }),
      (k) => ({ x: at.x - w - NOTE_GAP, y: at.y + k * (h + NOTE_GAP) }),
      (k) => ({ x: at.x + k * (w + NOTE_GAP), y: at.y + at.h + NOTE_GAP }),
      (k) => ({ x: at.x + k * (w + NOTE_GAP), y: at.y - h - NOTE_GAP }),
    ];
    let spot = null;
    for (let k = 0; k < 8 && !spot; k++)
      for (const option of options) {
        const candidate = option(k);
        if (!taken().some((other) => overlaps({ ...candidate, w, h }, other, NOTE_GAP / 2))) {
          spot = candidate;
          break;
        }
      }
    spot ??= { x: at.x, y: Math.max(...taken().map((r) => r.y + r.h), 0) + ROW_GAP };
    positions.set(note.id, spot);
    placedNotes.push({ ...spot, w, h });
  }
  return { positions, bounds: boundsOf(positions, sizes, frames) };
}

function boundsOf(positions, sizes, frames) {
  let bounds = null;
  const grow = (x, y, w, h) => {
    bounds = bounds
      ? { x0: Math.min(bounds.x0, x), y0: Math.min(bounds.y0, y), x1: Math.max(bounds.x1, x + w), y1: Math.max(bounds.y1, y + h) }
      : { x0: x, y0: y, x1: x + w, y1: y + h };
  };
  for (const [id, position] of positions) {
    const size = sizes.get(id);
    if (size) grow(position.x, position.y, size.width, size.height);
  }
  for (const frame of frames.values()) {
    const rect = frameRect(frame, positions, sizes);
    if (rect) grow(rect.x, rect.y, rect.w, rect.h);
  }
  return bounds ?? { x0: 0, y0: 0, x1: 1, y1: 1 };
}

/** The zoom that fits bounds in area, leaving a margin. */
export function fitZoom(bounds, area) {
  return Math.min(
    (area.width - 2 * FIT_PAD) / Math.max(1, bounds.x1 - bounds.x0),
    (area.height - 2 * FIT_PAD) / Math.max(1, bounds.y1 - bounds.y0),
  );
}

const AUTHORED_GAP = 40;
const SEARCH_STEP = 32;

/**
 * Where the page's own positions say, and the automatic layout's place for every box without one,
 * moved to the nearest spot that keeps AUTHORED_GAP round every placed box and leaves every frame
 * outline, as it would be with that box, clear of boxes that are not its members.
 */
function withAuthored(auto, level, authored) {
  const { sizes } = level;
  const frameDefs = level.frames ?? [];
  const notes = new Set(level.nodes.filter((n) => n.kind === "note").map((n) => n.id));
  const positions = new Map();
  for (const node of level.nodes) {
    const at = authored.get(node.id);
    if (at) positions.set(node.id, { x: at.x, y: at.y });
  }
  const rectOf = (id, p) => ({ x: p.x, y: p.y, w: sizes.get(id).width, h: sizes.get(id).height });
  const valid = (id, rect) => {
    const others = [...positions].filter(([other]) => other !== id).map(([other, p]) => [other, rectOf(other, p)]);
    if (others.some(([, r]) => overlaps(rect, r, AUTHORED_GAP))) return false;
    const all = new Map([...others, [id, rect]]);
    return frameDefs.every((frame) => {
      const members = frame.nodes.filter((m) => all.has(m)).map((m) => all.get(m));
      if (!members.length) return true;
      const outline = frameOutline(members);
      return [...all].every(([other, r]) => frame.nodes.includes(other) || notes.has(other) || !overlaps(outline, r, 16));
    });
  };
  const neighbours = (id) => {
    const linked = [...level.edges, ...(level.noteLinks ?? [])].flatMap((e) => (e.from === id ? [e.to] : e.to === id ? [e.from] : []));
    const mates = frameDefs.filter((f) => f.nodes.includes(id)).flatMap((f) => f.nodes);
    return [...linked, ...mates].filter((other) => positions.has(other));
  };
  for (const node of level.nodes) {
    if (positions.has(node.id) || !sizes.get(node.id)) continue;
    const { width: w, height: h } = sizes.get(node.id);
    const wanted = auto.positions.get(node.id);
    let spot = valid(node.id, { ...wanted, w, h }) ? wanted : null;
    const anchors = neighbours(node.id).map((other) => rectOf(other, positions.get(other)));
    if (!anchors.length && positions.size) anchors.push(...[...positions].map(([other, p]) => rectOf(other, p)));
    for (const anchor of anchors) {
      if (spot) break;
      const cx = anchor.x + anchor.w / 2 - w / 2;
      const cy = anchor.y + anchor.h / 2 - h / 2;
      for (let k = 1; k <= 24 && !spot; k++) {
        const ring = [];
        for (let i = -k; i <= k; i++)
          for (let j = -k; j <= k; j++)
            if (Math.max(Math.abs(i), Math.abs(j)) === k) ring.push({ x: cx + i * SEARCH_STEP, y: cy + j * SEARCH_STEP });
        ring.sort((a, b) => Math.hypot(a.x - cx, a.y - cy) - Math.hypot(b.x - cx, b.y - cy));
        spot = ring.find((c) => valid(node.id, { ...c, w, h })) ?? null;
      }
    }
    spot ??= { x: 0, y: Math.max(0, ...[...positions].map(([other, p]) => rectOf(other, p).y + rectOf(other, p).h)) + ROW_GAP };
    positions.set(node.id, { x: Math.round(spot.x), y: Math.round(spot.y) });
  }
  return positions;
}

/**
 * Layout a level with frames as structural blocks. A readable arrangement is preferred; if the
 * whole level is wider than the viewport, the path starts at readable zoom and the reader pans.
 * `level.authored` (id → { x, y }) holds the positions the page itself carries; a box with one stays
 * there, and the automatic layout places the rest round those.
 */
export function layoutLevel(level, area) {
  const authored = level.authored ?? new Map();
  const path = mainPath(level.edges);
  const frameDefs = level.frames ?? [];
  const frameByNode = new Map(frameDefs.flatMap((frame) => frame.nodes.map((id) => [id, frame])));
  const sizes = level.sizes;
  const frames = new Map(frameDefs.map((frame) => [frame.id, frame]));
  const blocks = new Map();
  for (const frame of frameDefs) {
    const block = blockFor(frame, sizes, level.edges, level.labelSize);
    if (block) blocks.set(frame.id, { id: frame.id, frame: true, nodes: frame.nodes, block, width: block.width, height: block.height });
  }
  const notes = level.nodes
    .filter((node) => node.kind === "note")
    .map((node) => ({
      id: node.id,
      size: sizes.get(node.id) ?? { width: 180, height: 64 },
      anchors: (level.noteLinks ?? []).flatMap((link) => (link.from === node.id ? [link.to] : link.to === node.id ? [link.from] : [])),
    }));
  for (const node of level.nodes.filter((node) => node.kind !== "note")) {
    if (frameByNode.has(node.id)) continue;
    const size = sizes.get(node.id) ?? { width: 180, height: 64 };
    blocks.set(node.id, { id: node.id, nodes: [node.id], width: size.width, height: size.height });
  }
  const byNode = new Map();
  for (const unit of blocks.values()) for (const id of unit.nodes) byNode.set(id, unit);
  const mainUnits = [];
  const seen = new Set();
  for (const id of path.spine) {
    const unit = byNode.get(id);
    if (unit && !seen.has(unit.id)) {
      seen.add(unit.id);
      mainUnits.push(unit);
    }
  }
  if (!mainUnits.length) {
    const first = blocks.values().next().value;
    if (first) mainUnits.push(first), seen.add(first.id);
  }
  const edgeRank = (unit) => {
    const step = level.edges
      .filter((edge) => edge.step !== null && (unit.nodes.includes(edge.from) || unit.nodes.includes(edge.to)))
      .map((edge) => edge.step);
    return step.length ? Math.min(...step) : Number.POSITIVE_INFINITY;
  };
  const sideUnits = [...blocks.values()]
    .filter((unit) => !seen.has(unit.id))
    .sort((a, b) => edgeRank(a) - edgeRank(b) || a.id.localeCompare(b.id));
  const unitInput = Object.assign([...mainUnits], {
    allSide: sideUnits,
    byNode,
    edges: level.edges,
    notes,
  });
  let best = null;
  for (let perRow = mainUnits.length; perRow >= 1; perRow--) {
    const attempt = arrange(perRow, unitInput, { sizes, frames, area, labelSize: level.labelSize });
    attempt.zoom = fitZoom(attempt.bounds, area);
    if (!best || attempt.zoom > best.zoom) best = attempt;
    if (attempt.zoom >= READABLE_ZOOM) break;
  }
  const positions = authored.size ? withAuthored(best, level, authored) : best.positions;
  const frameRects = new Map();
  for (const frame of frameDefs) {
    const rect = frameRect(frame, positions, sizes);
    if (rect) frameRects.set(frame.id, rect);
  }
  best.bounds = boundsOf(positions, sizes, frames);
  best.zoom = fitZoom(best.bounds, area);
  best.frames = frameRects;
  best.positions = positions;
  return best;
}
