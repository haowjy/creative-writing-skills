/*
 * What "correct" means for the router (js/routes.js): for every page of the engine's example atlas
 * and of a project atlas (when present), laid out and then with each box dragged to random
 * places, and for generated boxes, frames and arrows, every route must satisfy:
 *   1. no arrow touches a box that is not one of its ends, comes within CLEAR of one, or crosses a frame title;
 *   2. no arrow runs along a frame border within FRAME_CLEAR of it (it crosses a border squarely), and none
 *      runs along an end box except straight out of its side;
 *   3. an arrow leaves and enters its boxes squarely on a side, clear of the corners, and no two arrows
 *      run parallel and overlapping closer than MIN_APART;
 *   4. a label sits centred on a straight run of its own arrow, inside the run, and touches no box, frame title
 *      or border, other label, or any arrow's route but its own run.
 * Run: `node --test` in this engine directory (or `node --test tools/atlas/test/routes.test.mjs` from a project root).
 */
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { test } from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import { coversTitle, frameShapes, titleSpots } from "../js/frames.js";
import { layoutLevel } from "../js/layout.js";
import { loadLevelPages, parsePage, positionLines } from "../js/pages.js";
import { CLEAR, FRAME_CLEAR, PORT_MARGIN } from "../js/route-grid.js";
import { levelInput, routeArrows } from "../js/routes.js";

const here = dirname(fileURLToPath(import.meta.url));
// The project atlas to check besides the example: set ATLAS_CONFIG, else the design atlas of this machine.
const PROJECT = process.env.ATLAS_CONFIG ?? "/home/jimyao/.meridian/git/voluma-bio-docs/work/ideal-architecture/atlas.config.mjs";
const EPS = 0.5;
const MIN_APART = 7;
const LABEL_MARGIN = 10;

// ---- A seeded random source ----

function random(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---- Geometry ----

const gapBetween = (seg, r) => {
  const [x0, x1] = [Math.min(seg[0].x, seg[1].x), Math.max(seg[0].x, seg[1].x)];
  const [y0, y1] = [Math.min(seg[0].y, seg[1].y), Math.max(seg[0].y, seg[1].y)];
  const dx = Math.max(r.x - x1, x0 - (r.x + r.w), 0);
  const dy = Math.max(r.y - y1, y0 - (r.y + r.h), 0);
  return Math.hypot(dx, dy);
};
const crosses = (seg, r, pad = 0) => gapBetween(seg, r) <= pad;
const rectsOverlap = (a, b, pad = 0) =>
  a.x < b.x + b.w + pad && b.x < a.x + a.w + pad && a.y < b.y + b.h + pad && b.y < a.y + a.h + pad;
const horizontal = (s) => s[0].y === s[1].y;
const span = (s, axis) => [Math.min(s[0][axis], s[1][axis]), Math.max(s[0][axis], s[1][axis])];
const segmentsOf = (points) => points.slice(1).map((p, k) => [points[k], p]);

/** Asserts properties 1 to 4 for `routed`, the output of routeArrows(`input`); returns how many arrows had no exact route. */
function assertRoutes(input, routed, where) {
  const boxes = [...input.boxes].map(([id, r]) => ({ id, ...r }));
  const byId = new Map(boxes.map((b) => [b.id, b]));
  const outlines = input.frames.flatMap((f) => f.outlines);
  const titles = input.frames.map((f) => f.title);
  const borders = outlines.map((o) => ({
    horizontals: [o.y, o.y + o.h].map((y) => ({ y, x0: o.x, x1: o.x + o.w })),
    verticals: [o.x, o.x + o.w].map((x) => ({ x, y0: o.y, y1: o.y + o.h })),
  }));
  let inexact = 0;
  const all = routed.arrows.map((r, i) => ({ r, a: input.arrows[i], i, segs: segmentsOf(r.points) }));
  for (const { r, a, i, segs } of all) {
    const name = `${where}: arrow ${i} ${a.from}→${a.to}`;
    if (!r.exact) {
      inexact++;
      continue;
    }
    const [A, B] = [byId.get(a.from), byId.get(a.to)];
    // 1 and 2: boxes, titles, frame borders.
    segs.forEach((seg, k) => {
      for (const box of boxes) {
        if ((box === A && k === 0) || (box === B && k === segs.length - 1)) continue;
        assert.ok(gapBetween(seg, box) >= CLEAR - EPS, `${name}: segment ${k} is ${gapBetween(seg, box).toFixed(1)} from box ${box.id}`);
      }
      for (const t of titles)
        assert.ok(gapBetween(seg, t) >= FRAME_CLEAR - EPS, `${name}: segment ${k} touches a frame title`);
      for (const b of borders) {
        if (horizontal(seg)) {
          const [s0, s1] = span(seg, "x");
          for (const e of b.horizontals)
            if (Math.min(s1, e.x1) - Math.max(s0, e.x0) > 0)
              assert.ok(Math.abs(seg[0].y - e.y) >= FRAME_CLEAR - EPS, `${name}: segment ${k} runs along a frame border`);
        } else {
          const [s0, s1] = span(seg, "y");
          for (const e of b.verticals)
            if (Math.min(s1, e.y1) - Math.max(s0, e.y0) > 0)
              assert.ok(Math.abs(seg[0].x - e.x) >= FRAME_CLEAR - EPS, `${name}: segment ${k} runs along a frame border`);
        }
      }
    });
    // 3: squarely out of a side, clear of the corners.
    const squarely = (box, p, q) => {
      const onSide = [
        [p.y === box.y && q.x === p.x && q.y < p.y, p.x, box.x, box.w],
        [p.y === box.y + box.h && q.x === p.x && q.y > p.y, p.x, box.x, box.w],
        [p.x === box.x && q.y === p.y && q.x < p.x, p.y, box.y, box.h],
        [p.x === box.x + box.w && q.y === p.y && q.x > p.x, p.y, box.y, box.h],
      ];
      return onSide.some(([fits, v, lo, len]) => fits && v >= lo + PORT_MARGIN - EPS && v <= lo + len - PORT_MARGIN + EPS);
    };
    assert.ok(squarely(A, r.points[0], r.points[1]), `${name}: does not leave its box squarely`);
    assert.ok(squarely(B, r.points.at(-1), r.points.at(-2)), `${name}: does not enter its box squarely`);
  }
  // 3: no two arrows overlap along a run.
  for (const x of all) {
    if (!x.r.exact) continue;
    for (const y of all) {
      if (y.i <= x.i || !y.r.exact) continue;
      for (const s of x.segs)
        for (const t of y.segs) {
          if (horizontal(s) !== horizontal(t)) continue;
          const axis = horizontal(s) ? "x" : "y";
          const across = horizontal(s) ? "y" : "x";
          const [s0, s1] = span(s, axis);
          const [t0, t1] = span(t, axis);
          if (Math.min(s1, t1) - Math.max(s0, t0) > 0)
            assert.ok(Math.abs(s[0][across] - t[0][across]) >= MIN_APART, `${where}: arrows ${x.i} and ${y.i} run ${Math.abs(s[0][across] - t[0][across])}px apart`);
        }
    }
  }
  // 4: labels.
  const labels = all.filter(({ r }) => r.label);
  for (const { r, a, i, segs } of all) {
    if (a.label && r.exact) assert.ok(r.label, `${where}: arrow ${i} has no label place`);
    if (!r.label) continue;
    const name = `${where}: label of arrow ${i}`;
    const rect = r.label;
    const host = segs.findIndex((s) => {
      if (horizontal(s)) {
        const [s0, s1] = span(s, "x");
        return Math.abs(s[0].y - (rect.y + rect.h / 2)) < EPS && rect.x >= s0 + LABEL_MARGIN - EPS && rect.x + rect.w <= s1 - LABEL_MARGIN + EPS;
      }
      const [s0, s1] = span(s, "y");
      return Math.abs(s[0].x - (rect.x + rect.w / 2)) < EPS && rect.y >= s0 + LABEL_MARGIN - EPS && rect.y + rect.h <= s1 - LABEL_MARGIN + EPS;
    });
    assert.ok(host >= 0, `${name}: not centred on a run of its arrow`);
    for (const box of boxes) assert.ok(!rectsOverlap(rect, box), `${name}: covers box ${box.id}`);
    for (const t of titles) assert.ok(!rectsOverlap(rect, t), `${name}: covers a frame title`);
    for (const o of outlines)
      for (const edge of [
        { x: o.x, y: o.y, w: o.w, h: 0 },
        { x: o.x, y: o.y + o.h, w: o.w, h: 0 },
        { x: o.x, y: o.y, w: 0, h: o.h },
        { x: o.x + o.w, y: o.y, w: 0, h: o.h },
      ])
        assert.ok(!rectsOverlap(rect, edge), `${name}: sits on a frame border`);
    for (const other of labels) if (other.i !== i) assert.ok(!rectsOverlap(rect, other.r.label), `${name}: overlaps the label of arrow ${other.i}`);
    for (const other of all) {
      if (!other.r.exact) continue;
      other.segs.forEach((seg, k) => {
        if (other.i === i && k === host) return;
        assert.ok(!crosses(seg, rect), `${name}: covers a run of arrow ${other.i}`);
      });
    }
  }
  return inexact;
}

// ---- Pages ----

const wordsWidth = (text, em) => text.length * em;
const BOX_TEXT = /<br\s*\/?>/;

async function loadAtlas(configFile) {
  const config = (await import(pathToFileURL(configFile))).default;
  const root = resolve(dirname(configFile), config.root);
  const read = async (path) => readFileSync(join(root, path), "utf8");
  return loadLevelPages(read, config.pagesDir);
}

/** A page as the viewer lays it out, with box sizes from their text (the viewer measures them). */
function layoutPage(page, authored = new Map(page.mermaid.positions.map(({ id, x, y }) => [id, { x, y }]))) {
  const { nodes, frames = [], edges, noteLinks } = page.mermaid;
  const sizes = new Map(
    nodes.map((n) => {
      const [name, ...role] = n.label.replace(/<\/?small>/g, "").split(BOX_TEXT);
      // The viewer wraps a box's text at about 190px, so a long role makes a taller box, not a wider one.
      const text = n.kind === "note" ? Math.min(220, wordsWidth(n.label, 6.4)) : Math.min(190, Math.max(wordsWidth(name, 9), wordsWidth(role.join(" "), 6.6)));
      const roleLines = Math.max(1, Math.ceil(wordsWidth(role.join(" "), 6.6) / 190));
      return [n.id, { width: Math.ceil(text + 36), height: n.kind === "note" ? 56 : role.length ? 44 + 18 * roleLines : 44 }];
    }),
  );
  const labelSize = (e) => {
    const text = wordsWidth(e.label, 6.6);
    return { width: Math.ceil(Math.min(124, text) + 14), height: Math.ceil(Math.ceil(text / 124) * 16 + 8) };
  };
  const level = { nodes, frames, edges, noteLinks, sizes, labelSize, authored };
  const laid = layoutLevel(level, { width: 1280, height: 800 });
  const rects = new Map(nodes.map((n) => [n.id, { x: laid.positions.get(n.id).x, y: laid.positions.get(n.id).y, w: sizes.get(n.id).width, h: sizes.get(n.id).height }]));
  return { level, rects, labelSize, titleWidth: (label) => label.length * 8, sizes };
}

const inputFor = (p, rects) =>
  levelInput({
    rects,
    frames: frameShapes(p.level.frames, rects, p.titleWidth, new Set(p.level.nodes.filter((n) => n.kind === "note").map((n) => n.id))),
    edges: p.level.edges,
    noteLinks: p.level.noteLinks,
    labelSize: p.labelSize,
  });

/** Moves box `id` to a random place that leaves a gap round every other box and frame title. */
function drag(p, rects, id, rand) {
  const box = rects.get(id);
  const all = [...rects.values()];
  const x0 = Math.min(...all.map((r) => r.x)) - 150;
  const y0 = Math.min(...all.map((r) => r.y)) - 150;
  const x1 = Math.max(...all.map((r) => r.x + r.w)) + 150;
  const y1 = Math.max(...all.map((r) => r.y + r.h)) + 150;
  for (let tries = 0; tries < 200; tries++) {
    const moved = { ...box, x: x0 + rand() * (x1 - x0 - box.w), y: y0 + rand() * (y1 - y0 - box.h) };
    const others = new Map(rects);
    others.set(id, moved);
    const input = inputFor(p, others);
    const clear = [...others].every(([other, r]) => other === id || !rectsOverlap(moved, r, 2 * CLEAR + 12));
    const titleClear = input.frames.every((f) => !rectsOverlap(moved, f.title, 2 * CLEAR + 4));
    if (clear && titleClear) return others;
  }
  return rects;
}

async function pagesOf(configFile) {
  const { levels } = await loadAtlas(configFile);
  return [...levels.values()].filter((l) => l.page.mermaid?.type === "flowchart");
}

for (const [label, configFile] of [
  ["engine example", join(here, "../example/atlas.config.mjs")],
  ["project atlas", PROJECT],
]) {
  test(`${label}: every page routes cleanly, laid out and with boxes dragged about`, async (t) => {
    if (!existsSync(configFile)) return t.skip(`${configFile} is not here`);
    const rand = random(7);
    let routes = 0;
    for (const level of await pagesOf(configFile)) {
      const p = layoutPage(level.page);
      let rects = p.rects;
      const where = `${label} ${level.id}`;
      assert.equal(assertRoutes(inputFor(p, rects), routeArrows(inputFor(p, rects)), where), 0, `${where}: an arrow has no exact route`);
      routes++;
      for (const id of p.rects.keys())
        for (let k = 0; k < 2; k++) {
          rects = drag(p, rects, id, rand);
          const input = inputFor(p, rects);
          assert.equal(assertRoutes(input, routeArrows(input), `${where} (${id} dragged)`), 0, `${where}: an arrow has no exact route`);
          routes++;
        }
    }
    console.log(`  ${label}: ${routes} routings checked`);
  });
}

for (const [label, configFile] of [
  ["engine example", join(here, "../example/atlas.config.mjs")],
  ["project atlas", PROJECT],
]) {
  test(`${label}: no dragged box covers a frame title while a spot is free`, async (t) => {
    if (!existsSync(configFile)) return t.skip(`${configFile} is not here`);
    const rand = random(11);
    for (const level of await pagesOf(configFile)) {
      const p = layoutPage(level.page);
      if (!p.level.frames.length) continue;
      let rects = p.rects;
      const all = [...rects.values()];
      const x1 = Math.max(...all.map((r) => r.x + r.w));
      const y1 = Math.max(...all.map((r) => r.y + r.h));
      for (let k = 0; k < 120; k++) {
        const id = [...rects.keys()][Math.floor(rand() * rects.size)];
        const box = rects.get(id);
        rects = new Map(rects).set(id, { ...box, x: rand() * (x1 - box.w), y: rand() * (y1 - box.h) });
        const shapes = frameShapes(p.level.frames, rects, p.titleWidth);
        for (const f of shapes.values()) {
          const boxes = [...rects];
          const free = f.fractured
            ? titleSpots(f.members.map((m) => ({ ...m, x: f.x + m.x, y: f.y + m.y })), p.titleWidth(f.label)).some((spot) => !boxes.some(([, r]) => coversTitle(r, spot)))
            : true;
          if (free)
            for (const [other, r] of boxes)
              assert.ok(!coversTitle(r, f.title), `${label} ${level.id}: ${other} covers the title of ${f.label} after ${k + 1} drags`);
        }
      }
    }
  });
}

// ---- Generated cases ----

function generate(seed, boxCount, arrowCount, frameCount) {
  const rand = random(seed);
  const rects = new Map();
  const side = Math.sqrt(boxCount) * 330;
  for (let tries = 0; rects.size < boxCount && tries < 5000; tries++) {
    const r = { x: rand() * side, y: rand() * side * 0.7, w: 110 + rand() * 90, h: 44 + rand() * 30 };
    if ([...rects.values()].every((o) => !rectsOverlap(r, o, 2 * CLEAR + 24))) rects.set(`b${rects.size}`, r);
  }
  const ids = [...rects.keys()];
  const frames = [];
  const taken = new Set();
  for (let f = 0; f < frameCount; f++) {
    const seedBox = ids[Math.floor(rand() * ids.length)];
    if (taken.has(seedBox)) continue;
    const c = rects.get(seedBox);
    const members = ids.filter((id) => !taken.has(id) && Math.hypot(rects.get(id).x - c.x, rects.get(id).y - c.y) < 330).slice(0, 4);
    for (const id of members) taken.add(id);
    if (members.length > 1) frames.push({ id: `f${f}`, label: `Frame ${f}`, nodes: members });
  }
  const arrows = [];
  for (let k = 0; k < arrowCount; k++) {
    const from = ids[Math.floor(rand() * ids.length)];
    let to = ids[Math.floor(rand() * ids.length)];
    if (to === from) to = ids[(ids.indexOf(from) + 1) % ids.length];
    const chars = 6 + Math.floor(rand() * 40);
    arrows.push({ from, to, label: { width: Math.min(124, chars * 6.6) + 14, height: Math.ceil((chars * 6.6) / 124) * 16 + 8 }, step: k < arrowCount / 6 ? k + 1 : null });
  }
  const shapes = frameShapes(frames, rects, (label) => label.length * 8);
  const input = levelInput({ rects, frames: shapes, edges: [], noteLinks: [], labelSize: () => null });
  input.arrows = arrows;
  return input;
}

test("generated boxes, frames and arrows", () => {
  for (let seed = 1; seed <= 24; seed++) {
    const boxes = 6 + (seed % 5) * 4;
    const input = generate(seed, boxes, Math.min(2 * boxes, 8 + (seed % 7) * 6), seed % 4);
    const routed = routeArrows(input);
    assert.equal(assertRoutes(input, routed, `generated ${seed}`), 0, `generated ${seed}: an arrow has no exact route`);
  }
});

test("40 boxes and 80 arrows route fast enough to follow a drag", () => {
  const input = generate(99, 40, 80, 4);
  const started = performance.now();
  const routed = routeArrows(input);
  const ms = performance.now() - started;
  console.log(`  40 boxes, 80 arrows: ${ms.toFixed(0)} ms`);
  assert.equal(assertRoutes(input, routed, "40/80"), 0);
  assert.ok(ms < 4000, `${ms} ms`);
});

// ---- Authored positions ----

const flowchart = (...body) => ["# T", "", "```mermaid", "flowchart LR", '  a["A"]:::service', '  b["B"]:::service', ...body, "```"].join("\n");

test("a page's position lines parse, and a position for no box is reported with its line", () => {
  const ok = parsePage(flowchart("%% at a 0 0", "%% at b -40 120"));
  assert.deepEqual(ok.problems, []);
  assert.deepEqual(ok.mermaid.positions.map(({ id, x, y }) => [id, x, y]), [["a", 0, 0], ["b", -40, 120]]);
  assert.equal(parsePage(flowchart("%% at a 1.5 0")).problems.length, 1);
  assert.equal(parsePage(flowchart("%% at a 1 1", "%% at a 2 2")).problems.length, 1);
  assert.equal(parsePage(flowchart("%% only a comment")).problems.length, 0);
  assert.equal(positionLines(new Map([["a", { x: 10.4, y: 20 }], ["b", { x: 50, y: 70.6 }]])), "%% at a 0 0\n%% at b 40 51");
});

test("every page keeps its authored positions, places a box without one clear of the rest, and routes cleanly", async (t) => {
  const rand = random(11);
  for (const [label, configFile] of [["engine example", join(here, "../example/atlas.config.mjs")], ["project atlas", PROJECT]]) {
    if (!existsSync(configFile)) {
      t.diagnostic(`${configFile} is not here`);
      continue;
    }
    for (const level of await pagesOf(configFile)) {
      const where = `${label} ${level.id}`;
      const auto = layoutPage(level.page, new Map());
      const ids = [...auto.rects.keys()];
      const text = positionLines(new Map(ids.map((id) => [id, auto.rects.get(id)])));
      const full = parsePage(flowchart(text)); // the lines alone parse; ids are checked against the page below
      assert.deepEqual(full.problems, [], where);
      const authored = new Map(full.mermaid.positions.map(({ id, x, y }) => [id, { x, y }]));
      for (const missing of [null, ids[Math.floor(rand() * ids.length)], ids[0], ids.at(-1)]) {
        const subset = new Map(authored);
        subset.delete(missing);
        const p = layoutPage(level.page, subset);
        for (const [id, at] of subset) assert.deepEqual({ x: p.rects.get(id).x, y: p.rects.get(id).y }, at, `${where}: ${id} moved`);
        for (const a of ids)
          for (const b of ids)
            if (a < b) assert.ok(!rectsOverlap(p.rects.get(a), p.rects.get(b)), `${where}: ${a} and ${b} overlap (without ${missing})`);
        const input = inputFor(p, p.rects);
        assert.equal(assertRoutes(input, routeArrows(input), `${where} (without ${missing})`), 0, `${where}: an arrow has no exact route (without ${missing})`);
      }
    }
  }
});
