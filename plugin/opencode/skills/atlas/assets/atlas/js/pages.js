/*
 * Reads a map page (see README.md for the format). No DOM and no Node APIs, so the viewers and
 * check.mjs parse pages with the same code and cannot disagree about what a page says.
 */

export const NODE_KINDS = [
  "person",
  "client",
  "service",
  "store",
  "external",
  "files",
  "domain",
  "feature",
  "module",
  "package",
  "context",
  "group",
  "note",
];

/** The section list items each kind of page may carry. */
export const MAP_KEYS = [
  "Kind",
  "Paths",
  "Docs",
  "Machines",
  "Opens",
  "Breaks",
  "Drift",
  "See",
  "Keys",
  "Shot",
];
export const JOURNEY_KEYS = ["Map", "Machines", "Shot"];

const ID = "[A-Za-z][A-Za-z0-9_-]*";
// A hyphen joins two parts of an id; one before an arrow's dashes ("a-->>b") is the arrow's.
const SEQ_ID = "[A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z0-9_]+)*";
const LINE = {
  header: /^flowchart (?:LR|RL|TB|TD|BT)$/,
  subgraph: new RegExp(`^subgraph (${ID})\\["([^"]+)"\\]$`),
  end: /^end$/,
  node: new RegExp(`^(${ID})\\["([^"]*)"\\]:::(\\w+)$`),
  edge: new RegExp(`^(${ID}) (-->|<-->|-\\.->)\\|"([^"]+)"\\| (${ID})$`),
  noteLink: new RegExp(`^(${ID}) -\\.- (${ID})$`),
  sequenceHeader: /^sequenceDiagram$/,
  participant: new RegExp(`^(?:participant|actor) (${SEQ_ID})(?: as .+)?$`),
  message: new RegExp(`^(${SEQ_ID}) ?(?:-->>|->>|--x|-x|--\\)|-\\))[+-]? ?(${SEQ_ID}): .+$`),
  note: new RegExp(`^Note (?:over|left of|right of) (${SEQ_ID})(?:, ?(${SEQ_ID}))?: .+$`),
  activation: new RegExp(`^(?:activate|deactivate) (${SEQ_ID})$`),
  sequenceBlock: /^(?:loop|alt|opt|par|critical|break|rect|else|and|option)(?: .*)?$|^autonumber$/,
};
// A label may break lines and shrink a role line, nothing else.
const LABEL_TAGS = /<br\/>|<\/?small>/g;

/**
 * @typedef {{ line: number, message: string }} Problem
 * @returns {{
 *   title: string, view: string | null, intro: string,
 *   mermaid: null | {
 *     type: "flowchart" | "sequence" | null, source: string, line: number,
 *     nodes: {id, label, kind, line, frame: string | null}[], frames: {id, label, line, nodes: string[]}[],
 *     edges: {from, to, both, handedIn, label, step, line}[],
 *     noteLinks: {from, to, line}[],
 *     positions: {id, x, y, line}[],
 *     participants: {id, line}[],
 *   },
 *   sections: { id: string, line: number, paragraphs: string[], items: { key: string | null, value: string, line: number }[] }[],
 *   problems: Problem[],
 * }}
 */
export function parsePage(text) {
  const lines = text.split("\n");
  const page = { title: "", view: null, intro: "", mermaid: null, sections: [], problems: [] };
  const fail = (line, message) => page.problems.push({ line, message });
  let fence = null; // { length, kind: "mermaid" | "other" } inside a fenced block
  let section = null;
  let paragraph = [];
  const introParts = [];

  const endParagraph = () => {
    if (!paragraph.length) return;
    const joined = paragraph.join(" ");
    if (section) section.paragraphs.push(joined);
    else if (page.title) introParts.push(joined);
    paragraph = [];
  };

  for (const [i, raw] of lines.entries()) {
    const n = i + 1;
    const line = raw.trim();
    const marker = /^(`{3,})\s*(\S*)\s*$/.exec(line);
    if (fence) {
      if (marker && marker[1].length >= fence.length && !marker[2]) fence = null;
      else if (fence.kind === "mermaid") {
        parseMermaidLine(page.mermaid, line, n, fail);
        page.mermaid.source += `${line}\n`;
      }
      continue;
    }
    if (marker) {
      endParagraph();
      const kind = marker[2] === "mermaid" && !page.mermaid ? "mermaid" : "other";
      if (marker[2] === "mermaid") {
        if (page.mermaid) fail(n, "A second mermaid block: a page has one.");
        else
          page.mermaid = {
            type: null,
            source: "",
            line: n,
            nodes: [],
            frames: [],
            edges: [],
            noteLinks: [],
            positions: [],
            participants: [],
          };
      }
      fence = { length: marker[1].length, kind };
      continue;
    }
    const view = !section && /^- View:\s*(.*)$/.exec(line);
    if (view) {
      if (page.view !== null) fail(n, "A page has only one View line.");
      else if (!view[1]) fail(n, "A View line needs a value.");
      else page.view = view[1];
      continue;
    }
    const heading = /^(#{1,6}) (.+)$/.exec(line);
    if (heading) {
      endParagraph();
      if (heading[1] === "#" && !page.title) page.title = heading[2];
      else if (heading[1] === "##") {
        section = { id: heading[2], line: n, paragraphs: [], items: [] };
        page.sections.push(section);
      }
      continue;
    }
    if (!line) {
      endParagraph();
      continue;
    }
    if (section && line.startsWith("- ")) {
      endParagraph();
      const item = /^- ([A-Za-z]+): ?(.*)$/.exec(line);
      section.items.push(
        item
          ? { key: item[1], value: item[2], line: n }
          : { key: null, value: line.slice(2), line: n },
      );
      continue;
    }
    paragraph.push(line);
  }
  endParagraph();
  for (const frame of page.mermaid?.frames ?? [])
    if (frame.open) {
      fail(frame.line, `frame ${frame.id} has no matching end.`);
      for (const id of frame.nodes) {
        const node = page.mermaid.nodes.find((candidate) => candidate.id === id);
        if (node) node.frame = frame.id;
      }
      delete frame.open;
    }
  page.intro = introParts.join("\n\n");
  return page;
}

/**
 * The lines of a page's authored box positions, `%% at <id> <x> <y>`, one per box, for the boxes of
 * `positions` (id → { x, y } of the box's top-left corner in layout units). Shifted so the top-left
 * of the arrangement is 0, 0 and rounded, so the same arrangement always writes the same lines.
 */
export function positionLines(positions) {
  const at = [...positions];
  const x0 = Math.min(...at.map(([, p]) => p.x));
  const y0 = Math.min(...at.map(([, p]) => p.y));
  return at.map(([id, p]) => `%% at ${id} ${Math.round(p.x - x0)} ${Math.round(p.y - y0)}`).join("\n");
}

function parseMermaidLine(mermaid, line, n, fail) {
  if (!line) return;
  if (line.startsWith("%%")) {
    if (mermaid.type === "flowchart" && /^%% at(\s|$)/.test(line)) {
      const m = new RegExp(`^%% at (${ID}) (-?\\d+) (-?\\d+)$`).exec(line);
      if (!m) fail(n, "A position line is `%% at <box id> <x> <y>` with whole numbers.");
      else if (mermaid.positions.some((p) => p.id === m[1])) fail(n, `Box ${m[1]} has two positions.`);
      else mermaid.positions.push({ id: m[1], x: Number(m[2]), y: Number(m[3]), line: n });
    }
    return;
  }
  if (!mermaid.type) {
    if (LINE.header.test(line)) mermaid.type = "flowchart";
    else if (LINE.sequenceHeader.test(line)) mermaid.type = "sequence";
    else
      fail(
        n,
        `The mermaid block must start with a flowchart or sequenceDiagram header, not: ${line}`,
      );
    return;
  }
  if (mermaid.type === "sequence") return parseSequenceLine(mermaid, line, n, fail);
  const frame = LINE.subgraph.exec(line);
  if (frame) {
    if (mermaid.frames.some((candidate) => candidate.id === frame[1]) || mermaid.nodes.some((node) => node.id === frame[1])) {
      fail(n, `frame ${frame[1]} is declared more than once or conflicts with a box.`);
      return;
    }
    if (mermaid.frames.some((candidate) => candidate.open)) {
      fail(n, `nested frame ${frame[1]} is not supported; close the current frame first.`);
      return;
    }
    mermaid.frames.push({ id: frame[1], label: frame[2], line: n, nodes: [], open: true });
    return;
  }
  if (LINE.end.test(line)) {
    const open = mermaid.frames.find((candidate) => candidate.open);
    if (!open) fail(n, "end closes no frame.");
    else {
      delete open.open;
      for (const id of open.nodes) {
        const node = mermaid.nodes.find((candidate) => candidate.id === id);
        if (node) node.frame = open.id;
      }
    }
    return;
  }
  const open = mermaid.frames.find((candidate) => candidate.open);
  if (open) {
    const member = new RegExp(`^(${ID})$`).exec(line);
    if (member) {
      open.nodes.push(member[1]);
      return;
    }
  }
  let m = LINE.node.exec(line);
  if (m) {
    const bad = m[2].replace(LABEL_TAGS, "").match(/[<>]/);
    if (bad)
      fail(
        n,
        `Box ${m[1]}'s label holds "${bad[0]}": only <br/> and <small>...</small> are allowed.`,
      );
    if (open) open.nodes.push(m[1]);
    mermaid.nodes.push({ id: m[1], label: m[2], kind: m[3], line: n, frame: open?.id ?? null });
    return;
  }
  m = LINE.noteLink.exec(line);
  if (m) {
    mermaid.noteLinks.push({ from: m[1], to: m[2], line: n });
    return;
  }
  m = LINE.edge.exec(line);
  if (m) {
    const step = /^(\d+)\. /.exec(m[3]);
    mermaid.edges.push({
      from: m[1],
      to: m[4],
      both: m[2] === "<-->",
      // A dotted arrow is a dependency handed in (a port) or types alone, not a value import.
      handedIn: m[2] === "-.->",
      label: m[3],
      step: step ? Number(step[1]) : null,
      line: n,
    });
    return;
  }
  const tailOpen = mermaid.frames.find((candidate) => candidate.open);
  if (tailOpen) fail(n, `A mermaid line the format doesn't allow inside frame ${tailOpen.id}: ${line}`);
  else fail(n, `A mermaid line the format doesn't allow: ${line}`);
}

function parseSequenceLine(mermaid, line, n, fail) {
  const participants = (...ids) =>
    mermaid.participants.push(...ids.filter(Boolean).map((id) => ({ id, line: n })));
  const match = (re) => re.exec(line);
  const m =
    match(LINE.participant) ?? match(LINE.message) ?? match(LINE.note) ?? match(LINE.activation);
  if (m) participants(m[1], m[2]);
  else if (line === "end" || LINE.sequenceBlock.test(line)) return;
  else fail(n, `A sequenceDiagram line the format doesn't allow: ${line}`);
}

/**
 * The box a flow participant names: its id when one non-context box has it, else `<page>-<id>` (the
 * page file's name without .md, e.g. server-routes). `levels` is [{ id: page name, nodes }].
 * Returns { level, box } or { error }.
 */
export function resolveParticipant(levels, name) {
  const hits = levels.flatMap((l) =>
    l.nodes
      .filter((n) => n.kind !== "context" && (n.id === name || `${l.id}-${n.id}` === name))
      .map((n) => ({ level: l, box: n })),
  );
  const bare = hits.filter((h) => h.box.id === name);
  if (bare.length > 1)
    return {
      error: `participant ${name} is the id of boxes on ${bare.map((h) => h.level.id).join(", ")}: write <page>-${name}, e.g. ${bare[0].level.id}-${name}.`,
    };
  if (hits.length !== 1)
    return {
      error: hits.length
        ? `participant ${name} names ${hits.length} boxes.`
        : `participant ${name} isn't a box id on any level page.`,
    };
  return hits[0];
}

/** The item of a section with this key, or undefined. */
export const item = (section, key) => section.items.find((it) => it.key === key);

/** Backtick-quoted repo paths in a list value. */
export const pathsOf = (value) => [...value.matchAll(/`([^`]+)`/g)].map((m) => m[1]);

/** Markdown links in a list value: [{ label, href }]. */
export const linksOf = (value) =>
  [...value.matchAll(/\[([^\]]*)\]\(([^)\s]+)\)/g)].map((m) => ({ label: m[1], href: m[2] }));

const isUrl = (href) => /^[a-z][a-z0-9+.-]*:/i.test(href);

/** A relative `href` from the page at repo path `from`: { path, fragment }, path null for a URL or one that climbs out of the repo. */
export function resolveHref(from, href) {
  if (isUrl(href)) return { path: null, fragment: null, url: href };
  const [file, fragment = null] = href.split("#");
  const out = file === "" ? from.split("/") : from.split("/").slice(0, -1);
  if (file !== "") {
    for (const part of file.split("/")) {
      if (part === "..") {
        if (!out.length) return { path: null, fragment };
        out.pop();
      } else if (part !== "." && part !== "") out.push(part);
    }
  }
  return { path: out.join("/"), fragment };
}

const SHOT_REF = /^([a-z0-9-]+)(?:\/([a-z0-9-]+))?$/;

/**
 * What a `Shot` item names in the screens manifest (the config's `screens`): `<shot>` or
 * `<shot>/<region>`. Returns { name, shot, region } (`region` null when the ref names none), or
 * { error } saying what is missing.
 */
export function resolveShot(screens, ref) {
  const match = SHOT_REF.exec(ref);
  if (!match)
    return { error: `"${ref}" is not "<shot>" or "<shot>/<region>", in lowercase and hyphens` };
  const [, name, regionId] = match;
  const shot = screens?.[name];
  if (!shot) return { error: `no shot "${name}" in the screens manifest` };
  if (!regionId) return { name, shot, region: null };
  const region = shot.regions?.find((r) => r.id === regionId);
  if (!region) return { error: `shot "${name}" has no region "${regionId}"` };
  return { name, shot, region };
}

/** GitHub-style heading ids, so `page.md#heading` links land. */
export const slug = (text) =>
  text
    .toLowerCase()
    .replace(/<[^>]+>/g, "")
    .replace(/[^\p{L}\p{N}\s-]/gu, "")
    .trim()
    .replace(/\s/g, "-");

/** A glob as a RegExp over repo paths: `*` is part of one segment, `**` any depth (`**` + `/` also matches none). */
export function globRegExp(glob) {
  const source = glob
    .split(/(\*\*\/|\*\*|\*)/)
    .map((part) =>
      part === "**/"
        ? "(?:.*/)?"
        : part === "**"
          ? ".*"
          : part === "*"
            ? "[^/]*"
            : part.replace(/[.+?^${}()|[\]\\]/g, "\\$&"),
    )
    .join("");
  return new RegExp(`^${source}$`);
}

/** The directory at the start of `path` that a segment glob (`apps/*`, only `*`) matches, or null: the "unit" a file belongs to. */
export function unitOf(path, glob) {
  const depth = glob.split("/").length;
  const unit = path.split("/").slice(0, depth).join("/");
  return unit.split("/").length === depth && globRegExp(glob).test(unit) ? unit : null;
}

/** The text with the lines inside fenced code blocks blanked, so line numbers stay. */
export function withoutFences(text) {
  let fence = 0;
  return text
    .split("\n")
    .map((line) => {
      const marker = /^(`{3,})\s*(\S*)\s*$/.exec(line.trim());
      if (fence) {
        if (marker && marker[1].length >= fence && !marker[2]) fence = 0;
        return "";
      }
      if (marker) {
        fence = marker[1].length;
        return "";
      }
      return line;
    })
    .join("\n");
}

/** The level pages README.md lists under "## The pages": [{ id, title, href }], in order. */
export function levelLinks(readme) {
  const out = [];
  let inList = false;
  for (const line of withoutFences(readme).split("\n")) {
    if (line.startsWith("## ")) inList = line.trim() === "## The pages";
    const m = inList && /^- \[([^\]]*)\]\(([\w-]+)\.md\)/.exec(line);
    if (m) out.push({ id: m[2], title: m[1], href: `${m[2]}.md` });
  }
  return out;
}

/**
 * Every level page, the one set the viewer and check.mjs both use: the README's top levels, then
 * the page each box's `Opens` names, all in `mapDir`. `read(path)` returns a repo file's text. Each
 * top level is walked breadth-first before the next, so a page opened from two places keeps the
 * first parent found, System before Code, and a top level another one opens (Server, from System's
 * box) takes that parent too: its trail is where the reader drills in from.
 * Returns { roots: [{ id, title }], levels: Map id → { id, title, path, page, trail } } where
 * `title` is the name the nav and breadcrumb show (a top level's README label; a child's page title,
 * which loses its parent's "Server: " prefix here, as the heading the viewer shows does) and `trail` is the ancestors, root first: [{ title, hash }].
 */
export async function loadLevelPages(read, mapDir) {
  const roots = levelLinks(await read(`${mapDir}/README.md`));
  const labels = new Map(roots.map((r) => [r.id, r.title]));
  const levels = new Map();
  for (const r of roots) {
    const queue = [{ id: r.id, path: `${mapDir}/${r.href}`, trail: [] }];
    while (queue.length) {
      const { id, path, trail } = queue.shift();
      if (levels.has(id)) continue;
      const page = parsePage(await read(path));
      // The breadcrumb names the parent, so a child's shown title drops the "Server: " the .md heading keeps for GitHub readers.
      if (trail.length) page.title = page.title.replace(`${trail.at(-1).page}: `, "");
      const title = labels.get(id) ?? page.title;
      levels.set(id, { id, title, path, page, trail });
      for (const s of page.sections) {
        const opens = linksOf(item(s, "Opens")?.value ?? "")[0];
        const target = opens && resolveHref(path, opens.href).path;
        if (!target?.startsWith(`${mapDir}/`) || !target.endsWith(".md")) continue;
        queue.push({
          id: target.slice(mapDir.length + 1, -3),
          path: target,
          trail: [...trail, { title, page: page.title, hash: `#${id}`, box: s.id }],
        });
      }
    }
  }
  return { roots: roots.map((r) => ({ id: r.id, title: r.title })), levels };
}

/** Where the dark theme's tokens sit when a config names no token files: `default-tokens.css`'s. */
export const DEFAULT_DARK = { attribute: "data-theme", value: "dark" };
