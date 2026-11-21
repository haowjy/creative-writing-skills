/*
 * The geometry of frames (labelled outlines around boxes): how far a frame stands off its members,
 * where its label sits, and the shape a frame has for the boxes where they are now. A frame is derived
 * from its members whenever the map is drawn, never saved. No DOM.
 */

export const GROUP_TOP = 40;
export const GROUP_SIDE = 26;
export const GROUP_BOTTOM = 26;
/** A broken frame outlines each member this far out. */
export const MEMBER_OUTLINE = 4;

const overlaps = (a, b) => a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;

/** The outline of a frame around member rectangles [{ x, y, w, h }]. */
export function frameOutline(members) {
  const x = Math.min(...members.map((m) => m.x)) - GROUP_SIDE;
  const y = Math.min(...members.map((m) => m.y)) - GROUP_TOP;
  const x1 = Math.max(...members.map((m) => m.x + m.w)) + GROUP_SIDE;
  const y1 = Math.max(...members.map((m) => m.y + m.h)) + GROUP_BOTTOM;
  return { x, y, w: x1 - x, h: y1 - y };
}

const TITLE_HEIGHT = 14;
/** A box this close to a title counts as covering it. */
const TITLE_CLEAR = 4;

/** Where an unbroken frame's label sits (page.css: `.group-frame-label`), given its text's measured width. */
function insideTitle(outline, textWidth) {
  return { x: outline.x + 14, y: outline.y + 10, w: Math.min(textWidth + 10, outline.w - 28), h: TITLE_HEIGHT };
}

/** The spots a broken frame's label may take: round each member's outline, above it first. */
export function titleSpots(members, textWidth) {
  const w = textWidth + 10;
  const h = TITLE_HEIGHT;
  return members.flatMap((m) => {
    const x = m.x - MEMBER_OUTLINE + 10;
    const top = m.y - MEMBER_OUTLINE;
    return [
      { x, y: top - h, w, h },
      { x, y: m.y + m.h + MEMBER_OUTLINE, w, h },
      { x: m.x - MEMBER_OUTLINE - w, y: top, w, h },
      { x: m.x + m.w + MEMBER_OUTLINE, y: top, w, h },
    ];
  });
}

/** Whether a box lies on `spot`. */
export const coversTitle = (box, spot) =>
  overlaps(box, { x: spot.x - TITLE_CLEAR, y: spot.y - TITLE_CLEAR, w: spot.w + 2 * TITLE_CLEAR, h: spot.h + 2 * TITLE_CLEAR });

/**
 * Where a broken frame's label sits: the first of its spots no box covers, so a box dragged over
 * the frame never hides its name. When boxes cover every spot, the first is used.
 */
function memberTitle(members, rects, textWidth) {
  const spots = titleSpots(members, textWidth);
  return spots.find((spot) => ![...rects.values()].some((r) => coversTitle(r, spot))) ?? spots[0];
}

/**
 * Every frame as drawn, from `rects` (id → { x, y, w, h }) of the boxes: its outline, label, member
 * ids, `title` rect (as the label is drawn), `members` relative to the outline, and `fractured` when a box that is not a member lies
 * inside it, so it is drawn as a dashed outline round each member instead of one border. `noteIds`
 * are boxes that never break a frame; `titleWidth(label)` is a label's drawn width.
 */
export function frameShapes(frames, rects, titleWidth, noteIds = new Set()) {
  const shapes = new Map();
  for (const frame of frames) {
    const members = frame.nodes.map((id) => ({ id, rect: rects.get(id) })).filter((m) => m.rect);
    if (!members.length) continue;
    const outline = frameOutline(members.map((m) => m.rect));
    const fractured = [...rects].some(
      ([id, rect]) => !frame.nodes.includes(id) && !noteIds.has(id) && overlaps(rect, outline),
    );
    const textWidth = titleWidth(frame.label);
    shapes.set(frame.id, {
      ...outline,
      title: fractured ? memberTitle(members.map((m) => m.rect), rects, textWidth) : insideTitle(outline, textWidth),
      label: frame.label,
      nodes: frame.nodes,
      fractured,
      members: members.map(({ id, rect }) => ({ id, x: rect.x - outline.x, y: rect.y - outline.y, w: rect.w, h: rect.h })),
    });
  }
  return shapes;
}
