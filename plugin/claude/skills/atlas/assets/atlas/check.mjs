#!/usr/bin/env node
/**
 * Keeps an atlas from drifting silently from what it describes: `node check.mjs <path to atlas.config.mjs>`.
 * The project's own README.md says what each check catches and what it can't; this directory's
 * README.md has the config reference. Prints one line per problem, naming the page and the entry,
 * and exits 1 when there are any.
 */
import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, posix, relative, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { readImports, sourceFilesUnder, under, workspacePackages } from "./imports.mjs";
import {
  globRegExp,
  item,
  JOURNEY_KEYS,
  linksOf,
  loadLevelPages,
  MAP_KEYS,
  NODE_KINDS,
  parsePage,
  pathsOf,
  resolveHref,
  resolveParticipant,
  resolveShot,
  slug,
  unitOf,
  withoutFences,
} from "./js/pages.js";
import { readTokens, tokenSource } from "./tokens.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const configFile = resolve(process.argv[2] ?? "");
const config = (await import(pathToFileURL(configFile).href)).default;
const repo = resolve(dirname(configFile), config.root ?? ".");
const MAP_DIR = config.pagesDir;
const STATE_MACHINES_INDEX = config.stateMachines?.index;
const DEPENDENCIES = config.nav?.dependencies ? config.dependencies.page : null;
const JOURNEYS_ON = Boolean(config.nav?.journeys);
const problems = [];
const fail = (where, message) => problems.push(`${where}: ${message}`);
const read = (path) => readFileSync(join(repo, path), "utf8");

// ---- The pages ----

const dir = (path) =>
  existsSync(join(repo, path))
    ? readdirSync(join(repo, path))
        .filter((f) => f.endsWith(".md"))
        .sort()
    : [];
const levelFiles = dir(MAP_DIR).filter(
  (f) => !["README.md", "AGENTS.md", DEPENDENCIES].includes(f),
);
const flowFiles = JOURNEYS_ON ? dir(`${MAP_DIR}/flows`).filter((f) => f !== "index.md") : [];
const journeyFiles = JOURNEYS_ON ? dir(`${MAP_DIR}/journeys`).filter((f) => f !== "index.md") : [];
const hasFlows = flowFiles.length > 0;

/** @type {Map<string, ReturnType<typeof parsePage>>} repo path → parsed page */
const pages = new Map();
const load = (path) => {
  const page = parsePage(read(path));
  pages.set(path, page);
  return page;
};
const levels = levelFiles.map((f) => ({
  file: f,
  path: `${MAP_DIR}/${f}`,
  page: load(`${MAP_DIR}/${f}`),
}));
const flows = flowFiles.map((f) => ({
  file: `flows/${f}`,
  path: `${MAP_DIR}/flows/${f}`,
  page: load(`${MAP_DIR}/flows/${f}`),
}));
const journeys = journeyFiles.map((f) => ({
  file: `journeys/${f}`,
  path: `${MAP_DIR}/journeys/${f}`,
  page: load(`${MAP_DIR}/journeys/${f}`),
}));
for (const extra of [
  "README.md",
  DEPENDENCIES,
  ...(JOURNEYS_ON ? ["journeys/index.md"] : []),
  ...(hasFlows ? ["flows/index.md"] : []),
])
  if (extra) load(`${MAP_DIR}/${extra}`);
const nameOf = (path) => path.slice(MAP_DIR.length + 1);

for (const [path, page] of pages)
  for (const p of page.problems) fail(`${nameOf(path)}:${p.line}`, p.message);

// ---- Links: every relative link in every page resolves, and a `#id` lands on something ----

function headingIds(path) {
  const page = pages.get(path) ?? parsePage(read(path));
  const ids = new Set(page.sections.map((s) => s.id));
  for (const m of withoutFences(read(path)).matchAll(/^#{1,6} (.+)$/gm)) ids.add(slug(m[1]));
  return ids;
}

/** Checks one link from the page at `from`. */
function checkLink(from, line, href) {
  const { path, fragment, url } = resolveHref(from, href);
  if (url) return;
  const where = `${nameOf(from)}:${line}`;
  if (path === null) return void fail(where, `link ${href} climbs out of the repository.`);
  if (!existsSync(join(repo, path)))
    return void fail(where, `link ${href} points at ${path}, which doesn't exist.`);
  if (fragment && path.endsWith(".md") && !headingIds(path).has(fragment))
    fail(where, `link ${href} has no #${fragment} in ${path}.`);
}

for (const path of pages.keys()) {
  withoutFences(read(path))
    .replace(/`[^`\n]*`/g, "")
    .split("\n")
    .forEach((text, i) => {
      for (const { href } of linksOf(text)) checkLink(path, i + 1, href);
    });
}

// ---- Level pages ----

const isLevelPath = (path) => levelFiles.some((f) => `${MAP_DIR}/${f}` === path);
/** Every box on every page: { id, page, path, kind, paths, opens }. */
const boxes = [];

for (const { file, path, page } of levels) {
  if (!page.mermaid) {
    fail(file, "no mermaid block.");
    continue;
  }
  if (page.mermaid.type !== "flowchart") {
    if (page.mermaid.type) fail(`${file}:${page.mermaid.line}`, "a level page draws a flowchart.");
    continue;
  }
  const { nodes, edges } = page.mermaid;
  const nodeIds = new Set();
  for (const n of nodes) {
    if (nodeIds.has(n.id)) fail(`${file}:${n.line}`, `box ${n.id} is declared twice.`);
    nodeIds.add(n.id);
    if (!NODE_KINDS.includes(n.kind))
      fail(`${file}:${n.line}`, `box ${n.id} has unknown kind ${n.kind}.`);
  }
  const sectionIds = new Set();
  for (const s of page.sections) {
    if (sectionIds.has(s.id)) fail(`${file}:${s.line}`, `section ## ${s.id} appears twice.`);
    sectionIds.add(s.id);
    if (!nodeIds.has(s.id))
      fail(`${file}:${s.line}`, `section ## ${s.id} has no box in the diagram.`);
  }
  for (const n of nodes)
    if (n.kind !== "note" && !sectionIds.has(n.id))
      fail(`${file}:${n.line}`, `box ${n.id} has no ## ${n.id} section.`);
  const kindOf = new Map(nodes.map((n) => [n.id, n.kind]));
  for (const s of page.sections)
    if (kindOf.get(s.id) === "note") fail(`${file}:${s.line}`, `note ${s.id} takes no ## section.`);
  for (const l of page.mermaid.noteLinks) {
    for (const end of [l.from, l.to])
      if (!nodeIds.has(end))
        fail(
          `${file}:${l.line}`,
          `note link ${l.from} -.- ${l.to} names ${end}, which isn't a box.`,
        );
    if (
      nodeIds.has(l.from) &&
      nodeIds.has(l.to) &&
      (kindOf.get(l.from) === "note") === (kindOf.get(l.to) === "note")
    )
      fail(`${file}:${l.line}`, `note link ${l.from} -.- ${l.to} must join a note to a box.`);
  }
  for (const n of nodes)
    if (n.kind === "note" && !page.mermaid.noteLinks.some((l) => l.from === n.id || l.to === n.id))
      fail(`${file}:${n.line}`, `note ${n.id} links to nothing: add "${n.id} -.- <box>".`);
  for (const e of edges) {
    for (const end of [e.from, e.to])
      if (kindOf.get(end) === "note")
        fail(
          `${file}:${e.line}`,
          `arrow ${e.from} to ${e.to} touches note ${end}: a note joins a box only by "-.-".`,
        );
    for (const end of [e.from, e.to])
      if (!nodeIds.has(end))
        fail(`${file}:${e.line}`, `arrow ${e.from} to ${e.to} names ${end}, which isn't a box.`);
    const kind = /^(http|ws|sql|model|files|call|port|import): /.exec(e.label);
    if (kind)
      fail(
        `${file}:${e.line}`,
        `arrow ${e.from} to ${e.to} starts with "${kind[1]}:": arrows carry words, not kinds, and none says "import" (${DEPENDENCIES ?? "the dependencies page"} lists the broken rules).`,
      );
  }
  const steps = edges.filter((e) => e.step !== null);
  steps.forEach((e, i) => {
    if (e.step !== i + 1)
      fail(
        `${file}:${e.line}`,
        `the numbered arrows must run 1, 2, 3 in order; this one is ${e.step}, expected ${i + 1}.`,
      );
  });

  for (const s of page.sections) {
    const node = nodes.find((n) => n.id === s.id);
    if (!node || node.kind === "note") continue;
    const where = `${file}:${s.id}`;
    for (const it of s.items)
      if (!MAP_KEYS.includes(it.key))
        fail(
          `${file}:${it.line}`,
          `${s.id} has a list item that isn't one of ${MAP_KEYS.join(", ")}: ${it.key ?? it.value}`,
        );
    const kind = item(s, "Kind");
    if (!kind) fail(where, `no "Kind" item.`);
    else if (NODE_KINDS.includes(node.kind) && kind.value !== node.kind)
      fail(
        `${file}:${kind.line}`,
        `${s.id} says Kind: ${kind.value} but the diagram's class is ${node.kind}.`,
      );
    if (!s.paragraphs.length) fail(where, "no sub line (the first paragraph).");
    const paths = [];
    const opens = [];
    for (const it of s.items) {
      if (it.key === "Paths" && node.kind === "group")
        fail(
          `${file}:${it.line}`,
          `${s.id} is a group: it takes no Paths; its child page's boxes cover the code.`,
        );
      else if (it.key === "Paths") {
        for (const p of pathsOf(it.value)) {
          if (existsSync(join(repo, p))) paths.push(p);
          else fail(`${file}:${it.line}`, `${s.id} names ${p}, which doesn't exist.`);
        }
      }
      if (it.key === "Opens") {
        for (const l of linksOf(it.value)) {
          const target = resolveHref(path, l.href).path;
          if (target && !isLevelPath(target))
            fail(`${file}:${it.line}`, `${s.id} Opens ${l.href}, which isn't a level page.`);
          else if (target) opens.push(target);
        }
      }
    }
    if (node.kind === "group" && !item(s, "Opens"))
      fail(where, `a group box needs "Opens: [label](child.md)".`);
    if (node.kind === "context" && !item(s, "See"))
      fail(where, `a context box needs "See: [label](page.md#id)".`);
    boxes.push({ id: s.id, page: file, path, kind: node.kind, paths, opens });
  }
}
const levelNodes = levels.map((l) => ({
  id: l.file.slice(0, -3),
  nodes: l.page.mermaid?.nodes ?? [],
}));

// ---- Journeys ----

const indexLinks = JOURNEYS_ON
  ? linksOf(read(`${MAP_DIR}/journeys/index.md`)).map(
      (l) => resolveHref(`${MAP_DIR}/journeys/index.md`, l.href).path,
    )
  : [];
for (const j of journeys)
  if (!indexLinks.includes(j.path)) fail("journeys/index.md", `doesn't link ${j.file}.`);
const readme = read(`${MAP_DIR}/README.md`);
// The viewer's own loader, so both agree on which level pages exist and what opens them.
const reachable = (
  await loadLevelPages(async (p) => (existsSync(join(repo, p)) ? read(p) : ""), MAP_DIR)
).levels;
for (const l of levels)
  if (![...reachable.values()].some((r) => r.path === l.path))
    fail(l.file, "is neither listed in README.md's pages nor opened by a box's Opens.");
for (const target of [
  hasFlows && "flows/index.md",
  DEPENDENCIES,
  JOURNEYS_ON && "journeys/index.md",
].filter(Boolean))
  if (!linksOf(readme).some((l) => l.href === target)) fail("README.md", `doesn't link ${target}.`);

const traced = new Set();
for (const { file, path, page } of journeys) {
  if (!page.sections.length) fail(file, "has no steps (## sections).");
  for (const s of page.sections) {
    for (const field of ["Does", "Sees"])
      if (!s.paragraphs.some((p) => p.startsWith(`${field}:`)))
        fail(`${file}:${s.id}`, `step has no "${field}:" paragraph.`);
    for (const it of s.items) {
      if (!JOURNEY_KEYS.includes(it.key))
        fail(
          `${file}:${it.line}`,
          `step "${s.id}" has a list item that isn't one of ${JOURNEY_KEYS.join(", ")}: ${it.key ?? it.value}`,
        );
      if (it.key !== "Map") continue;
      for (const l of linksOf(it.value)) {
        const target = resolveHref(path, l.href);
        const flow = flows.find((f) => f.path === target.path);
        if (flow) {
          traced.add(flow.path);
          continue;
        }
        const level = levels.find((lv) => lv.path === target.path);
        if (!level)
          fail(
            `${file}:${it.line}`,
            `step "${s.id}" Map link ${l.href} isn't a level page or a flow.`,
          );
        else if (
          !target.fragment ||
          !level.page.mermaid?.nodes.some((n) => n.id === target.fragment)
        )
          fail(`${file}:${it.line}`, `step "${s.id}" Map link ${l.href} must end in #<box id>.`);
      }
    }
  }
}

// ---- Screens ----
// The manifest (the config's `screens`): each shot's image exists, each region has bounds, and its `map` names a box on a
// level page and its `code` a repo path. Every `Shot` item on a box or journey step names a shot (and region) it holds.

let screens = null;
if (config.screens) {
  const at = config.screens;
  try {
    screens = JSON.parse(read(at));
  } catch (error) {
    fail(at, `doesn't read as JSON: ${error.message}`);
  }
  // With `serveSource: false` the viewer opens only the pages directory and `docs`: the manifest and its images must be there.
  const shown = (path) =>
    path.startsWith(`${MAP_DIR}/`) || (config.docs ?? []).some((g) => globRegExp(g).test(path));
  if (config.serveSource === false && !shown(at))
    fail(at, "isn't under the pages directory or matched by `docs`, so the viewer can't open it.");
  for (const [name, shot] of Object.entries(screens ?? {})) {
    const where = `${at}: shot ${name}`;
    const number = (v) => Number.isFinite(v) && v >= 0;
    if (typeof shot.title !== "string" || !shot.title) fail(where, "has no title.");
    if (!number(shot.width) || !number(shot.height) || !shot.width || !shot.height)
      fail(where, "needs a width and a height in pixels.");
    const image = typeof shot.image === "string" ? resolveHref(at, shot.image).path : null;
    if (!image || !existsSync(join(repo, image)))
      fail(where, `image ${shot.image} doesn't exist beside the manifest.`);
    else if (config.serveSource === false && !shown(image))
      fail(
        where,
        `image ${image} isn't under the pages directory or matched by \`docs\`, so the viewer can't show it.`,
      );
    const ids = new Set();
    for (const region of Array.isArray(shot.regions) ? shot.regions : []) {
      const here = `${where}, region ${region.id}`;
      if (!/^[a-z0-9-]+$/.test(region.id ?? ""))
        fail(here, "needs an id in lowercase and hyphens.");
      if (ids.has(region.id)) fail(here, "appears twice.");
      ids.add(region.id);
      if (typeof region.label !== "string" || !region.label) fail(here, "has no label.");
      if (![region.x, region.y, region.w, region.h].every(number) || !region.w || !region.h)
        fail(here, "needs x, y, w and h in pixels.");
      else if (region.x + region.w > shot.width || region.y + region.h > shot.height)
        fail(here, "reaches past the image.");
      if (region.code !== undefined && !existsSync(join(repo, region.code)))
        fail(here, `code ${region.code} doesn't exist.`);
      if (region.map !== undefined) {
        const [pageId, boxId, ...extra] = String(region.map).split("/");
        const level = levelNodes.find((l) => l.id === pageId);
        if (extra.length || !level)
          fail(here, `map ${region.map} isn't "<page>/<box>" on a level page.`);
        else if (!level.nodes.some((n) => n.id === boxId && n.kind !== "note"))
          fail(here, `map ${region.map}: ${pageId} has no box ${boxId}.`);
      }
    }
    if (!ids.size) fail(where, "has no regions.");
  }
}
const shotItems = [...levels, ...journeys].flatMap(({ file, page }) =>
  page.sections.flatMap((s) =>
    s.items.filter((it) => it.key === "Shot").map((it) => ({ file, s, it })),
  ),
);
for (const { file, s, it } of shotItems) {
  const where = `${file}:${it.line}`;
  if (!config.screens)
    fail(where, `${s.id} has a Shot, and the config has no \`screens\` manifest.`);
  else if (screens) {
    const found = resolveShot(screens, it.value);
    if (found.error) fail(where, `${s.id} Shot: ${found.error}.`);
  }
}

// ---- Flows ----

const flowIndexLinks = hasFlows
  ? linksOf(read(`${MAP_DIR}/flows/index.md`)).map(
      (l) => resolveHref(`${MAP_DIR}/flows/index.md`, l.href).path,
    )
  : [];
for (const f of flows) {
  if (!flowIndexLinks.includes(f.path)) fail("flows/index.md", `doesn't link ${f.file}.`);
  if (!traced.has(f.path))
    fail(
      f.file,
      "is not linked from any journey step's Map line, so the viewer can't reach it from Journeys.",
    );
  const m = f.page.mermaid;
  if (m?.type !== "sequence") fail(f.file, "has no sequenceDiagram.");
  for (const p of m?.participants ?? []) {
    const hit = resolveParticipant(levelNodes, p.id);
    if (hit.error) fail(`${f.file}:${p.line}`, hit.error);
  }
  if (!/^\d+\. /m.test(withoutFences(read(f.path))))
    fail(f.file, "has no numbered steps under the diagram.");
}

// ---- State machine pages ----

const indexed = new Set();
const attached = new Set();
let written = [];
if (config.stateMachines) {
  if (!existsSync(join(repo, STATE_MACHINES_INDEX))) fail(STATE_MACHINES_INDEX, "doesn't exist.");
  else {
    for (const match of read(STATE_MACHINES_INDEX).matchAll(/\]\(([^)\s#]+\.md)(?:#[^)]*)?\)/g)) {
      if (!/^[a-z]+:/i.test(match[1]))
        indexed.add(posix.join(posix.dirname(STATE_MACHINES_INDEX), match[1]));
    }
  }
  for (const { path, page } of levels)
    for (const s of page.sections)
      for (const it of s.items.filter((i) => i.key === "Machines"))
        for (const l of linksOf(it.value)) attached.add(resolveHref(path, l.href).path);
  for (const page of indexed) {
    if (!existsSync(join(repo, page)))
      fail(STATE_MACHINES_INDEX, `links ${page}, which doesn't exist.`);
    else if (/state-machine[^/]*\.md$/.test(page) && !attached.has(page))
      fail(STATE_MACHINES_INDEX, `${page} is on no box: add it to a box's Machines.`);
  }
  written = execFileSync(
    "git",
    [
      "ls-files",
      "-z",
      "--cached",
      "--others",
      "--exclude-standard",
      "--",
      config.stateMachines.pages,
    ],
    { cwd: repo, encoding: "utf8" },
  )
    .split("\0")
    .filter(Boolean);
  for (const page of written) {
    if (page !== STATE_MACHINES_INDEX && existsSync(join(repo, page)) && !indexed.has(page))
      fail(page, `isn't linked by ${STATE_MACHINES_INDEX}: add it to the index.`);
  }
}

// ---- Coverage ----
// From git, not the disk: a branch switch leaves untracked node_modules or build output behind.

const roots = [...new Set(boxes.flatMap((b) => b.paths))];
const FILE_RULES = (config.dependencies?.rules ?? []).filter((r) => r.files);
const gitFiles = execFileSync(
  "git",
  ["ls-files", "-z", "--cached", "--others", "--exclude-standard"],
  { cwd: repo, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 },
)
  .split("\0")
  .filter(Boolean);
// Segment globs match one directory depth (`unitOf`); a `**` in one would match nothing and pass silently.
const segmentGlobs = [
  ["services.glob", config.services ? [config.services.glob] : []],
  ["coverage", (config.coverage ?? []).map((c) => c.glob)],
  ["imports.workspaces", config.imports?.workspaces ?? []],
  [
    "dependencies.rules",
    (config.dependencies?.rules ?? [])
      .filter((r) => !r.files)
      .flatMap((r) => [r.cycle, r.from, r.to].filter(Boolean)),
  ],
];
for (const [key, globs] of segmentGlobs)
  for (const glob of globs)
    if (glob.includes("**"))
      fail(
        `config ${key}`,
        `"${glob}" has a "**", which these globs don't support: use "*" for one path segment.`,
      );
/** Directories matching a segment glob that hold tracked files (a file directly in the pattern's depth is not one). */
const directoriesMatching = (glob) => [
  ...new Set(
    gitFiles
      .filter((f) => f.split("/").length > glob.split("/").length)
      .map((f) => unitOf(f, glob))
      .filter(Boolean),
  ),
];

// A service is a directory matching the services glob: the top page has a box whose Paths are inside it and whose Opens is
// the page named after it (apps/www → www.md).
if (config.services) {
  for (const directory of directoriesMatching(config.services.glob)) {
    const name = directory.split("/").at(-1);
    const page = `${MAP_DIR}/${name}.md`;
    if (
      !boxes.some(
        (b) =>
          b.page === config.services.page &&
          b.opens.includes(page) &&
          b.paths.some((p) => under(p, directory)),
      )
    )
      fail(
        config.services.page,
        `${directory} needs a box on ${config.services.page} whose Paths are inside it and whose "Opens" is ${name}.md, a page of its own boxes (the project's README.md says how to add a service).`,
      );
  }
}
for (const { glob, needs } of config.coverage ?? []) {
  for (const directory of directoriesMatching(glob)) {
    if (needs && !existsSync(join(repo, directory, needs))) continue;
    if (!roots.some((p) => under(p, directory)))
      fail(
        "map",
        `${directory} is in no box's Paths: add a box for it, or a path to the box that holds it.`,
      );
  }
}

// ---- Dependencies ----
// The dependencies page lists the places the code breaks the configured rules, one row per break. The rows and
// the breaks the check computes from value imports must match one to one; ordinary imports are listed nowhere.
// A file rule (`files`, `to`) is a second table on the same page, one row per importing file and module, and counts
// type-only imports too.

const rules = config.dependencies?.rules ?? [];
const rows = [];
/** One entry per break the code has: key → { rule, from, to, files: the importing files }. For a unit rule, type-only imports are no run-time coupling and don't count. For a file rule, `from` is the importing file and `to` the module. */
const breaks = new Map();
const workspaceDirs = (config.imports?.workspaces ?? [])
  .flatMap(directoriesMatching)
  .filter((d) => existsSync(join(repo, d, "package.json")));
const importOptions = { workspaceDirs, aliases: config.imports?.aliases ?? [] };
const imports =
  DEPENDENCIES || config.arrows?.imports ? readImports(repo, roots, importOptions) : [];
if (DEPENDENCIES) {
  // Read apart from `imports`: a `files` directory outside every box must not feed the unit rules.
  const fileImports = readImports(
    repo,
    FILE_RULES.map((r) => r.files),
    importOptions,
  );
  const packages = workspacePackages(repo, workspaceDirs);

  const addBreak = (rule, from, to, file) => {
    const key = `${rule}|${from}|${to}`;
    if (!breaks.has(key)) breaks.set(key, { rule, from, to, files: new Set() });
    breaks.get(key).files.add(file);
  };
  const nameOf = (unit) => unit.split("/").at(-1);
  /**
   * A file rule's `to` entries as { name, reaches }: a workspace package (also reached by a path into its directory), a
   * package subpath (matched on the specifier as written) or a tracked repo path (matched on where the import resolves
   * to, named by its last segment). An entry that is none of these would pin nothing.
   */
  const fileTargets = (rule) => {
    const targets = [];
    for (const entry of rule.to) {
      if (packages.has(entry))
        targets.push({ name: entry, reaches: (i) => under(i.to, packages.get(entry)) });
      else if ([...packages.keys()].some((name) => entry.startsWith(`${name}/`)))
        targets.push({
          name: entry,
          reaches: (i) => i.spec === entry || i.spec.startsWith(`${entry}/`),
        });
      else if (gitFiles.some((f) => under(f, entry)))
        targets.push({ name: nameOf(entry), reaches: (i) => under(i.to, entry) });
      else
        fail(
          "config dependencies.rules",
          `"${rule.rule}": to ${entry} is no workspace package, package subpath or tracked path.`,
        );
    }
    if (new Set(targets.map((t) => t.name)).size < targets.length)
      fail(
        "config dependencies.rules",
        `"${rule.rule}": two "to" entries share a last segment, which would merge their rows.`,
      );
    return targets;
  };
  // Breaks name a unit by its last path segment, so two units of one glob with the same one would merge their rows.
  const unitRules = rules.filter((r) => !r.files);
  for (const glob of new Set(unitRules.flatMap((r) => [r.cycle, r.from, r.to].filter(Boolean)))) {
    const seen = new Map();
    for (const unit of directoriesMatching(glob)) {
      const other = seen.get(nameOf(unit));
      if (other) {
        fail(
          "config dependencies.rules",
          `"${glob}" matches both ${other} and ${unit}, which share the name "${nameOf(unit)}" in the breaks table: narrow the glob so each unit has its own last segment.`,
        );
        break;
      }
      seen.set(nameOf(unit), unit);
    }
  }
  /** How a break of each rule reads in a failure. */
  const describe = (b) => {
    const rule = rules.find((r) => r.rule === b.rule);
    if (rule.files) return `${rule.files}/${b.from} importing ${b.to}`;
    return rule.cycle
      ? `${b.from} importing ${b.to} inside a cycle`
      : `${b.from} importing ${b.to}`;
  };
  for (const rule of rules) {
    if (rule.files) {
      if (!existsSync(join(repo, rule.files)))
        fail("config dependencies.rules", `"${rule.rule}": files ${rule.files} doesn't exist.`);
      const targets = fileTargets(rule);
      for (const i of fileImports) {
        if (!under(i.from, rule.files)) continue;
        const file = i.from.slice(rule.files.length + 1);
        for (const t of targets) if (t.reaches(i)) addBreak(rule.rule, file, t.name, file);
      }
    } else if (rule.cycle) {
      const graph = new Map();
      const edgeFiles = new Map();
      for (const i of imports) {
        if (i.typeOnly) continue;
        const from = unitOf(i.from, rule.cycle);
        const to = unitOf(i.to, rule.cycle);
        if (!from || !to || from === to) continue;
        if (!graph.has(from)) graph.set(from, new Set());
        graph.get(from).add(to);
        edgeFiles.set(`${from}|${to}`, [...(edgeFiles.get(`${from}|${to}`) ?? []), i.from]);
      }
      const component = stronglyConnected(graph);
      for (const [from, targets] of graph)
        for (const to of targets)
          if (component.get(from) === component.get(to))
            for (const file of edgeFiles.get(`${from}|${to}`))
              addBreak(rule.rule, nameOf(from), nameOf(to), file);
    } else {
      for (const i of imports) {
        const from = unitOf(i.from, rule.from);
        const to = unitOf(i.to, rule.to);
        if (!i.typeOnly && from && to && from !== to)
          addBreak(rule.rule, nameOf(from), nameOf(to), i.from);
      }
    }
  }

  const TABLES = [
    { name: "unit", header: ["from", "to", "rule", "example file"], needed: true },
    // With several file rules the third column says which one a row is of; with one, the section heading does.
    ...(FILE_RULES.length
      ? [
          {
            name: "file",
            header: FILE_RULES.length > 1 ? ["file", "imports", "rule"] : ["file", "imports"],
            needed: true,
          },
        ]
      : []),
  ];
  const seen = new Set();
  let table = null;
  withoutFences(read(`${MAP_DIR}/${DEPENDENCIES}`))
    .split("\n")
    .forEach((text, i) => {
      if (!text.trim().startsWith("|")) return;
      const cells = text
        .trim()
        .replace(/^\||\|$/g, "")
        .split("|")
        .map((c) => c.trim().replaceAll("`", ""));
      if (cells.every((c) => /^:?-+:?$/.test(c))) return;
      const header = TABLES.find((t) => t.header[0] === cells[0].toLowerCase());
      if (header) {
        table = header;
        if (cells.map((c) => c.toLowerCase()).join("|") !== header.header.join("|"))
          fail(
            `${DEPENDENCIES}:${i + 1}`,
            `the table header must be: | ${header.header.join(" | ")} |`,
          );
        else seen.add(header.name);
        return;
      }
      rows.push({ cells, line: i + 1, table });
    });
  for (const t of TABLES)
    if (t.needed && !seen.has(t.name))
      fail(DEPENDENCIES, `has no ${t.name} table (| ${t.header.join(" | ")} |).`);

  const matched = new Set();
  for (const row of rows) {
    const where = `${DEPENDENCIES}:${row.line}`;
    if (!row.table) {
      fail(where, "a table row above any table header.");
      continue;
    }
    const isFile = row.table.name === "file";
    const known = rules.filter((r) => Boolean(r.files) === isFile).map((r) => r.rule);
    if (row.cells.length !== row.table.header.length) {
      fail(where, `a row has ${row.table.header.length} cells: ${row.table.header.join(", ")}.`);
      continue;
    }
    const [from, to, rule = FILE_RULES[0].rule, example = from] = row.cells;
    if (!known.includes(rule)) {
      fail(where, `rule "${rule}" isn't one of: ${known.join("; ")}.`);
      continue;
    }
    const key = `${rule}|${from}|${to}`;
    const found = breaks.get(key);
    if (matched.has(key)) fail(where, `${from} to ${to} (${rule}) has two rows.`);
    else if (!found)
      fail(
        where,
        `stale row: ${from} to ${to} is no break of "${rule}" today. Delete the row${isFile ? "" : "; `from` and `to` name the last segment of the directory (a single unit)"}.`,
      );
    else if (!found.files.has(example))
      fail(
        where,
        `example file ${example} doesn't break "${rule}" from ${from} to ${to}${existsSync(join(repo, example)) ? "" : " (it doesn't exist)"}; one that does: ${[...found.files][0]}.`,
      );
    matched.add(key);
  }
  for (const [key, b] of breaks)
    if (!matched.has(key))
      fail(
        DEPENDENCIES,
        `new break, a regression of "${b.rule}": ${describe(b)}${rules.find((r) => r.rule === b.rule).files ? "" : ` (${[...b.files][0]})`}. Remove the import first; add a row only if the break is accepted.`,
      );
}

/** Tarjan: node → component number; nodes in one cycle share one, and a lone node gets its own. */
function stronglyConnected(adjacency) {
  const index = new Map();
  const low = new Map();
  const onStack = new Set();
  const stack = [];
  const result = new Map();
  let counter = 0;
  let components = 0;
  const visit = (v) => {
    index.set(v, counter);
    low.set(v, counter++);
    stack.push(v);
    onStack.add(v);
    for (const w of adjacency.get(v) ?? []) {
      if (!index.has(w)) {
        visit(w);
        low.set(v, Math.min(low.get(v), low.get(w)));
      } else if (onStack.has(w)) low.set(v, Math.min(low.get(v), index.get(w)));
    }
    if (low.get(v) === index.get(v)) {
      let w;
      do {
        w = stack.pop();
        onStack.delete(w);
        result.set(w, components);
      } while (w !== v);
      components++;
    }
  };
  for (const v of adjacency.keys()) if (!index.has(v)) visit(v);
  return result;
}

// ---- Arrows between code ----
// With `arrows.imports`, a solid arrow between two code boxes needs a value import behind it: some file under the
// from box's Paths imports, by value, a file under the to box's Paths (either way for "<-->"; tests don't count). A
// type-only import doesn't: a dependency handed in is drawn dotted, and a dotted arrow is held to no import. A code
// box (also a reference one, which Opens another page) with no source under its Paths fails its solid arrows: give
// it Paths, or draw them dotted.

if (config.arrows?.imports) {
  const CODE_KINDS = ["domain", "feature", "module", "package"];
  const hasSource = new Map(boxes.map((b) => [b, sourceFilesUnder(repo, b.paths).size > 0]));
  const importedBy = (from, to) =>
    imports.some(
      (i) =>
        from.paths.some((p) => under(i.from, p)) &&
        i.reached.some((r) => !r.typeOnly && to.paths.some((p) => under(r.to, p))),
    );
  for (const { file, page } of levels)
    for (const e of page.mermaid?.edges ?? []) {
      if (e.handedIn) continue;
      const from = boxes.find((b) => b.page === file && b.id === e.from);
      const to = boxes.find((b) => b.page === file && b.id === e.to);
      if (!from || !to || ![from, to].every((b) => CODE_KINDS.includes(b.kind))) continue;
      const arrow = `arrow ${e.from} ${e.both ? "<-->" : "-->"} ${e.to}`;
      const bare = [from, to].find((b) => !hasSource.get(b));
      if (bare)
        fail(
          `${file}:${e.line}`,
          `${arrow}: ${bare.id} has no source files under its Paths to check it against. Give it Paths, or draw the arrow dotted.`,
        );
      else if (!importedBy(from, to) && !(e.both && importedBy(to, from)))
        fail(
          `${file}:${e.line}`,
          `${arrow}: no file under ${from.paths.join(", ")} imports a value from ${to.paths.join(", ")}. Draw it dotted if ${e.to} is handed in or only its types are used, or remove it.`,
        );
    }
}

// ---- The engine copy ----

// The project's copy of this engine matches the /atlas skill's, where the skill is installed
// (.mars/ is not committed, so CI skips this). A fix goes to the skill, not to the copy.
{
  const skill = join(repo, ".mars/skills/atlas/assets/atlas");
  if (existsSync(skill) && resolve(skill) !== resolve(here)) {
    const files = (dir, at = "") =>
      readdirSync(join(dir, at), { withFileTypes: true }).flatMap((entry) => {
        const path = at ? `${at}/${entry.name}` : entry.name;
        if (path === "example" || path === "node_modules") return [];
        return entry.isDirectory() ? files(dir, path) : [path];
      });
    const ours = new Set(files(here));
    const theirs = files(skill);
    const differ = theirs.filter(
      (f) => !ours.has(f) || readFileSync(join(here, f), "utf8") !== readFileSync(join(skill, f), "utf8"),
    );
    differ.push(...[...ours].filter((f) => !theirs.includes(f)));
    if (differ.length)
      fail(
        relative(repo, here) || ".",
        `differs from the /atlas skill's engine (${differ.slice(0, 3).join(", ")}${differ.length > 3 ? ", …" : ""}). Copy it again: rm -rf ${relative(repo, here)} && cp -r .mars/skills/atlas/assets/atlas ${relative(repo, here)}`,
      );
  }
}

// ---- Colours ----

// Only the token files hold a colour; the page sheet paints with --map-* roles, each of which the
// config maps to a token, or mixes from such roles itself.
const source = tokenSource(config, repo);
const tokens = readTokens(source.root, source.tokens);
for (const block of tokens.missing) fail("tokens", `${block}: no such block.`);
{
  const css = readFileSync(join(here, "styles/page.css"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
  const own = new Set([...css.matchAll(/(--[\w-]+)\s*:/g)].map((m) => m[1].slice(2)));
  const mapped = source.tokens.roles ?? {};
  const used = new Set();
  const raw = css.match(/#[0-9a-fA-F]{3,8}\b|\b(?:oklch|oklab|rgba?|hsla?|hwb|lab|lch)\(/g);
  if (raw) fail("styles/page.css", `holds a raw colour (${raw[0]}): use a --map-* role.`);
  for (const match of css.matchAll(/var\(\s*--([\w-]+)\s*(,)?/g)) {
    const [, name, fallback] = match;
    if (own.has(name) || fallback) continue;
    if (name.startsWith("map-")) used.add(name.slice(4));
    else fail("styles/page.css", `uses --${name}: it paints with --map-* roles only.`);
  }
  // The scripts read roles too (Mermaid's theme).
  for (const file of readdirSync(join(here, "js")))
    for (const [, name] of readFileSync(join(here, "js", file), "utf8").matchAll(
      /"--map-([\w-]+)"/g,
    ))
      if (!own.has(`map-${name}`)) used.add(name);
  for (const role of used)
    if (!(role in mapped))
      fail(
        "tokens.roles",
        `${role}: styles/page.css paints with --map-${role}, and no token is mapped to it.`,
      );
  for (const [role, token] of Object.entries(mapped)) {
    if (!used.has(role))
      fail("tokens.roles", `${role}: no such role (the viewer uses ${[...used].join(", ")}).`);
    else if (!tokens.names.has(token.replace(/^--/, "")))
      fail("tokens.roles", `${role}: ${token} is not defined by the token files.`);
  }
}

if (problems.length) {
  console.error(`atlas: ${problems.length} problem${problems.length === 1 ? "" : "s"}`);
  for (const problem of problems) console.error(`  ${problem}`);
  process.exit(1);
}
const edgeCount = levels.reduce((n, l) => n + (l.page.mermaid?.edges.length ?? 0), 0);
console.log(
  `atlas: ${levels.length} levels, ${boxes.length} boxes, ${edgeCount} arrows, ${flows.length} flows, ${rows.length} break rows, ${journeys.length} journeys, ${imports.length} imports read, ${attached.size} state machine pages on boxes, ${written.length} state machine pages, all in the index`,
);
