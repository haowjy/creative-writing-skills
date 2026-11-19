/*
 * The map view of a level page: its flowchart drawn with React Flow under the page's intro, and a
 * side panel with the selected box's section. A box's own arrows stay lit and the rest fade; a
 * group opens its child page. Boxes drag and the arrows follow; where they were put is remembered
 * for this page on this computer.
 */

import { storageKey } from "./config.js";
import { fitZoom, layoutLevel, READABLE_ZOOM } from "./layout.js";
import { paintInline, pathLink, route } from "./markdown.js";
import { item, linksOf, NODE_KINDS, pathsOf } from "./pages.js";
import { routeLevel } from "./routes.js";
import { shotCrop, shotView } from "./screens.js";
import { el } from "./shell.js";

const React = globalThis.React;
const h = React.createElement;
const RF = globalThis.ReactFlow;
const { createContext, Fragment, useContext, useEffect, useMemo, useRef, useState } = React;

/** A small level is drawn no larger than this at Fit. */
const MAX_FIT_ZOOM = 1.1;
/** Text width at which an arrow's label wraps. */
const LABEL_WRAP = 124;
const LAYOUT_KEY = `${storageKey("layout-v2")}:`;

const parts = (label) => {
  const [name, ...role] = label.split(/<br\s*\/?>/);
  const text = (html) => html.replace(/<[^>]+>/g, "");
  return { name: text(name), role: text(role.join(" ")) };
};
const plain = (label) => parts(label).name;

/** Where the reader dragged this page's boxes: { id: { x, y } }, or {} (no storage, or nothing saved). */
function savedLayout(path) {
  try {
    const saved = JSON.parse(localStorage.getItem(LAYOUT_KEY + path));
    return saved && typeof saved === "object" && !Array.isArray(saved) ? saved : {};
  } catch {
    return {};
  }
}

function saveLayout(path, positions) {
  try {
    if (positions) localStorage.setItem(LAYOUT_KEY + path, JSON.stringify(positions));
    else localStorage.removeItem(LAYOUT_KEY + path);
  } catch {
    // Not remembered; the boxes stay where they are for this visit.
  }
}

/**
 * The drawn size of an arrow's label, { width, height }, before it is drawn: layout and routing
 * need it to keep labels clear. The font and padding come from the label's own CSS.
 */
function labelMeasurer() {
  const context = document.createElement("canvas").getContext("2d");
  const styleOf = (className) => {
    const probe = el(
      "div",
      { class: className, style: "position:absolute;visibility:hidden" },
      "x",
    );
    document.body.append(probe);
    const s = getComputedStyle(probe);
    const px = (v) => Number.parseFloat(v) || 0;
    const style = {
      font: `${s.fontWeight} ${s.fontSize} ${s.fontFamily}`,
      line: px(s.lineHeight),
      padX: px(s.paddingLeft) + px(s.paddingRight) + px(s.borderLeftWidth) + px(s.borderRightWidth),
      padY: px(s.paddingTop) + px(s.paddingBottom) + px(s.borderTopWidth) + px(s.borderBottomWidth),
    };
    probe.remove();
    return style;
  };
  const styles = { step: styleOf("arrow-label is-step"), side: styleOf("arrow-label") };
  const cache = new Map();
  return (edge) => {
    const key = `${edge.step !== null}:${edge.label}`;
    if (cache.has(key)) return cache.get(key);
    const style = edge.step !== null ? styles.step : styles.side;
    context.font = style.font;
    const lines = [];
    for (const word of edge.label.split(/\s+/)) {
      const tried = lines.length ? `${lines.at(-1)} ${word}` : word;
      if (lines.length && context.measureText(tried).width <= LABEL_WRAP)
        lines[lines.length - 1] = tried;
      else lines.push(word);
    }
    const text = Math.max(...lines.map((l) => context.measureText(l).width));
    // Two pixels spare, so the browser's own wrapping never breaks a line the canvas kept whole.
    const size = {
      width: Math.ceil(text) + 2 + style.padX,
      height: Math.ceil(lines.length * style.line + style.padY),
    };
    cache.set(key, size);
    return size;
  };
}

/** What a box needs to draw itself that isn't in its node: the selection. */
const Selection = createContext({ selectedId: null, linked: new Set() });

// Arrows draw their own paths (routes.js); a box keeps one handle each way only because React Flow
// draws no edge without them.
const handles = () => [
  h(RF.Handle, { key: "in", type: "target", position: RF.Position.Top, isConnectable: false }),
  h(RF.Handle, { key: "out", type: "source", position: RF.Position.Bottom, isConnectable: false }),
];

function Box({ data, id }) {
  const { selectedId, linked } = useContext(Selection);
  const { node } = data;
  const { name, role } = parts(node.label);
  const state =
    selectedId === null
      ? ""
      : id === selectedId
        ? "is-selected"
        : linked.has(id)
          ? "is-linked"
          : "is-dim";
  return h(
    "div",
    {
      className: `card kind-${node.kind} ${state}`,
      title: data.opens ? "Opens its own page" : undefined,
    },
    ...handles(),
    h("div", { className: "card-label" }, name, data.opens ? " ▸" : ""),
    role ? h("div", { className: "card-sub" }, role) : null,
  );
}

function Note({ data, id }) {
  const { selectedId, linked } = useContext(Selection);
  return h(
    "div",
    { className: `note-card ${selectedId !== null && !linked.has(id) ? "is-dim" : ""}` },
    ...handles(),
    parts(data.node.label).name,
  );
}

const nodeTypes = { box: Box, note: Note };

function Arrow({ data, markerEnd, markerStart }) {
  if (!data.route) return null;
  const { d, label } = data.route;
  return h(
    Fragment,
    null,
    h(RF.BaseEdge, { path: d, markerEnd, markerStart, interactionWidth: 0 }),
    label &&
      h(
        RF.EdgeLabelRenderer,
        null,
        h(
          "div",
          {
            className: data.labelClass,
            style: {
              transform: `translate(${label.x}px, ${label.y}px)`,
              width: label.w,
              height: label.h,
            },
          },
          data.text,
        ),
      ),
  );
}

const edgeTypes = { arrow: Arrow };

/** The arrowheads every edge refers to by id, coloured from tokens by CSS. */
function Markers() {
  const arrow = (id) =>
    h(
      "marker",
      {
        key: id,
        id,
        viewBox: "0 0 10 10",
        refX: 9,
        refY: 5,
        markerWidth: 7,
        markerHeight: 7,
        orient: "auto-start-reverse",
        markerUnits: "strokeWidth",
      },
      h("path", { d: "M0,0 L10,5 L0,10 Z", className: id }),
    );
  return h(
    "svg",
    { className: "marker-defs", "aria-hidden": true, width: 0, height: 0 },
    h("defs", null, arrow("arch-arrow"), arrow("arch-arrow-step")),
  );
}

/** Fit the whole level when its text stays readable; otherwise show its start at a readable size, to pan. */
function fitLevel(flow, bounds, area) {
  if (!bounds || !area.width) return;
  const fit = Math.min(fitZoom(bounds, area), MAX_FIT_ZOOM);
  const zoom = Math.max(fit, READABLE_ZOOM);
  const [w, hgt] = [(bounds.x1 - bounds.x0) * zoom, (bounds.y1 - bounds.y0) * zoom];
  const x = w <= area.width ? (area.width - w) / 2 : 16;
  const y = hgt <= area.height ? (area.height - hgt) / 2 : 16;
  flow.setViewport({ x: x - bounds.x0 * zoom, y: y - bounds.y0 * zoom, zoom });
}

function Flow({ page, path, selectedId, onChoose, labelSize }) {
  const { nodes: sourceNodes, edges: sourceEdges, noteLinks } = page.mermaid;
  const flow = RF.useReactFlow();
  const initial = useMemo(
    () =>
      sourceNodes.map((node) => ({
        id: node.id,
        type: node.kind === "note" ? "note" : "box",
        position: { x: 0, y: 0 },
        data: {
          node,
          opens: Boolean(
            page.sections.find((s) => s.id === node.id)?.items.some((it) => it.key === "Opens"),
          ),
        },
        style: { visibility: "hidden" },
      })),
    [sourceNodes],
  );
  const [nodes, setNodes, onNodesChange] = RF.useNodesState(initial);
  const area = RF.useStore(
    (state) => ({ width: state.width, height: state.height }),
    (a, b) => a.width === b.width && a.height === b.height,
  );
  const measured = RF.useNodesInitialized();
  // Laid out once per drawing area and per Reset; a drag only changes positions, never this key.
  const [placement, setPlacement] = useState({ key: null, reset: 0, hints: new Map() });
  const areaKey = `${area.width}x${area.height}:${placement.reset}`;
  const areaNow = useRef(area);
  areaNow.current = area;

  useEffect(() => {
    if (!measured || placement.key === areaKey || !area.width) return;
    const sizes = new Map(flow.getNodes().map((n) => [n.id, n.measured]));
    const { positions, hints } = layoutLevel(
      { nodes: sourceNodes, edges: sourceEdges, noteLinks, sizes, labelSize },
      area,
    );
    const saved = savedLayout(path);
    const useSaved = sourceNodes.every(
      (n) => Number.isFinite(saved[n.id]?.x) && Number.isFinite(saved[n.id]?.y),
    );
    setNodes((current) =>
      current.map((n) => ({
        ...n,
        position: useSaved ? saved[n.id] : positions.get(n.id),
        style: {},
      })),
    );
    setPlacement((p) => ({ ...p, key: areaKey, hints }));
  }, [
    measured,
    placement.key,
    areaKey,
    area,
    flow,
    sourceNodes,
    sourceEdges,
    noteLinks,
    path,
    setNodes,
    labelSize,
  ]);

  const linked = useMemo(() => {
    const ids = new Set();
    for (const e of sourceEdges)
      if (e.from === selectedId || e.to === selectedId) ids.add(e.from).add(e.to);
    for (const l of noteLinks)
      if (l.from === selectedId || l.to === selectedId) ids.add(l.from).add(l.to);
    return ids;
  }, [sourceEdges, noteLinks, selectedId]);

  const touches = (e) => selectedId !== null && (e.from === selectedId || e.to === selectedId);
  const rects = useMemo(
    () =>
      placement.key &&
      new Map(
        nodes.map((n) => [
          n.id,
          { x: n.position.x, y: n.position.y, w: n.measured.width, h: n.measured.height },
        ]),
      ),
    [placement.key, nodes],
  );
  const route = (labelled) =>
    routeLevel({
      rects,
      edges: sourceEdges,
      noteLinks,
      hints: placement.hints,
      labelSize,
      labelled,
    });
  // Fit frames the level with every label, whichever box is chosen.
  const whole = useMemo(
    () => rects && route(() => true),
    [rects, placement.hints, sourceEdges, noteLinks, labelSize],
  );
  // With a box chosen, its own arrows' labels are the ones shown.
  const routes = useMemo(
    () => (selectedId === null ? whole : rects && route((i) => touches(sourceEdges[i]))),
    [whole, rects, selectedId],
  );
  const bounds = useRef(null);
  bounds.current = whole?.bounds;

  useEffect(() => {
    if (!placement.key) return;
    const frame = requestAnimationFrame(() => fitLevel(flow, bounds.current, areaNow.current));
    return () => cancelAnimationFrame(frame);
  }, [placement.key, flow]);

  const edges = useMemo(
    () => [
      ...sourceEdges.map((edge, i) => {
        const step = edge.step !== null;
        const marker = step ? "arch-arrow-step" : "arch-arrow";
        return {
          id: `e${i}`,
          type: "arrow",
          source: edge.from,
          target: edge.to,
          data: {
            route: routes?.arrows[i],
            text: edge.label,
            labelClass: `arrow-label ${step ? "is-step" : ""}`,
          },
          className: [
            "edge",
            step ? "is-step" : "",
            edge.handedIn ? "is-handed-in" : "",
            touches(edge) ? "is-lit" : "",
            selectedId !== null && !touches(edge) ? "is-faded" : "",
          ].join(" "),
          markerEnd: marker,
          markerStart: edge.both ? marker : undefined,
          focusable: false,
          selectable: false,
        };
      }),
      ...noteLinks.map((l, i) => ({
        id: `n${i}`,
        type: "arrow",
        source: l.from,
        target: l.to,
        data: { route: routes && { d: routes.links[i].d, label: null } },
        className: `edge note-link ${selectedId !== null && !linked.has(l.from) && !linked.has(l.to) ? "is-faded" : ""}`,
        focusable: false,
        selectable: false,
      })),
    ],
    [sourceEdges, noteLinks, selectedId, linked, routes],
  );

  const reset = () => {
    saveLayout(path, null);
    setPlacement((p) => ({ ...p, key: null, reset: p.reset + 1 }));
  };

  return h(
    Selection.Provider,
    { value: { selectedId, linked } },
    h(
      RF.ReactFlow,
      {
        nodes,
        edges,
        nodeTypes,
        edgeTypes,
        onNodesChange,
        onNodeClick: (_, node) => node.type === "box" && onChoose(node.id),
        onNodeDragStop: () =>
          saveLayout(path, Object.fromEntries(flow.getNodes().map((n) => [n.id, n.position]))),
        onPaneClick: () => onChoose(null),
        nodesDraggable: true,
        nodesConnectable: false,
        elementsSelectable: false,
        minZoom: 0.15,
        maxZoom: 2,
        proOptions: { hideAttribution: true },
        "aria-label": `${page.title} diagram`,
      },
      h(RF.Background, { variant: RF.BackgroundVariant.Dots, gap: 20, size: 1 }),
      h(RF.Controls, { showInteractive: false, showFitView: false, position: "bottom-right" }),
      h(
        RF.Panel,
        { position: "top-left", className: "diagram-tools" },
        h(
          "button",
          {
            type: "button",
            className: "text-button",
            onClick: () => fitLevel(flow, bounds.current, areaNow.current),
          },
          "Fit",
        ),
        h(
          "button",
          {
            type: "button",
            className: "text-button",
            onClick: reset,
            title: "Put the boxes back where the layout places them",
          },
          "Reset layout",
        ),
      ),
    ),
  );
}

/**
 * Mounts the map of `page` (parsed, at repo `path`) into `host`. `nav.go(hash)` opens another
 * route; `nav.replace(hash)` changes the address without a history entry. Returns { select(id), dispose() }.
 */
export function createMap(host, { page, path, nav, screens }) {
  let selected = null;
  const canvas = el("div", { class: "canvas" });
  const diagram = el("div", { class: "diagram", id: "map-diagram" });
  const panel = el("aside", { class: "panel", "aria-label": "Selected box" });
  canvas.append(intro(), diagram);
  host.replaceChildren(canvas, panel);

  const flowHost = el("div", { class: "flow" });
  diagram.append(flowHost, legend());
  const root = globalThis.ReactDOM.createRoot(flowHost);
  const labelSize = labelMeasurer();
  const drawn = () => {
    root.render(
      h(
        RF.ReactFlowProvider,
        null,
        h(Markers),
        h(Flow, { page, path, selectedId: selected, onChoose: choose, labelSize }),
      ),
    );
  };

  function intro() {
    const text = el("p", { class: "intro-text is-clamped" });
    paintInline(text, page.intro, path);
    const more = el(
      "button",
      {
        type: "button",
        class: "link-button more",
        onclick: () =>
          (more.textContent = text.classList.toggle("is-clamped") ? "Read more" : "Show less"),
      },
      "Read more",
    );
    return el(
      "details",
      { class: "intro", open: !matchMedia("(max-width: 719px)").matches },
      el("summary", null, el("strong", null, page.title)),
      text,
      more,
      el(
        "p",
        { class: "how-to" },
        el("strong", null, "How to read this: "),
        "follow the numbered arrows in order; thin arrows are side paths. Click a box for its detail. A box marked ▸ opens its own page. Drag a box to move it.",
      ),
    );
  }

  function legend() {
    const kinds = NODE_KINDS.filter((kind) => page.mermaid?.nodes.some((n) => n.kind === kind));
    return el(
      "details",
      { class: "legend" },
      el("summary", null, "Legend"),
      el(
        "ul",
        null,
        kinds.map((kind) => el("li", null, el("span", { class: `swatch kind-${kind}` }), kind)),
      ),
    );
  }

  /** A click on a box: a box with Opens goes to that page, any other box is selected (and put in the address). */
  function choose(id) {
    const opens = id && opensOf(id);
    if (opens) return nav.go(opens);
    nav.replace(
      id ? `${location.hash.split("/")[0]}/${encodeURIComponent(id)}` : location.hash.split("/")[0],
    );
    select(id);
  }

  function opensOf(id) {
    const section = page.sections.find((s) => s.id === id);
    const link = linksOf(item(section, "Opens")?.value ?? "")[0];
    return link && route(path, link.href)?.href;
  }

  // ---- The panel ----

  function select(id) {
    selected = id;
    drawn();
    panel.replaceChildren(id ? boxPanel(id) : overview());
    panel.scrollTop = 0;
  }

  function paragraph(markdown, className) {
    const p = el("p", { class: className });
    paintInline(p, markdown, path);
    return p;
  }

  /** Nothing selected: the boxes of this page, each with its one-line role, as a way in. */
  function overview() {
    return el(
      "div",
      { class: "panel-body" },
      el("h2", null, "Boxes on this page"),
      el(
        "ul",
        { class: "box-list" },
        page.mermaid.nodes
          .filter((n) => n.kind !== "note")
          .map((n) => {
            const section = page.sections.find((s) => s.id === n.id);
            return el(
              "li",
              null,
              el(
                "button",
                { type: "button", class: "link-button", onclick: () => choose(n.id) },
                plain(n.label),
                opensOf(n.id) ? " ▸" : "",
              ),
              section?.paragraphs[0] && paragraph(section.paragraphs[0], "sub-line"),
            );
          }),
      ),
    );
  }

  function boxPanel(id) {
    const section = page.sections.find((s) => s.id === id);
    const node = page.mermaid.nodes.find((n) => n.id === id);
    if (!section || !node)
      return el(
        "div",
        { class: "panel-body" },
        el("p", { class: "doc-note" }, `No box "${id}" on this page.`),
      );
    const [sub, ...about] = section.paragraphs;
    const value = (key) => item(section, key)?.value;
    const paths = pathsOf(value("Paths") ?? "");
    return el("div", { class: "panel-body" }, [
      el(
        "button",
        { type: "button", class: "link-button back", onclick: () => choose(null) },
        "← All boxes",
      ),
      el(
        "div",
        { class: "panel-head" },
        el("h2", null, plain(node.label)),
        el("span", { class: `chip kind-${node.kind}` }, node.kind),
      ),
      sub && paragraph(sub, "sub"),
      ...about.map((text) => paragraph(text)),
      value("Shot") && shotCrop(screens, value("Shot")),
      ...section.items
        .filter((it) => it.key === "Breaks" || it.key === "Drift")
        .map((it) =>
          el(
            "div",
            { class: `callout is-${it.key.toLowerCase()}` },
            el(
              "strong",
              null,
              it.key === "Breaks" ? "Breaks a rule: " : "Docs and code disagree: ",
            ),
            inline(it.value),
          ),
        ),
      paths.length
        ? el(
            "section",
            null,
            el("h3", null, "Paths"),
            el(
              "ul",
              { class: "paths" },
              paths.map((p) => el("li", null, pathLink(p))),
            ),
          )
        : null,
      value("Keys") &&
        el("section", null, el("h3", null, "Keys it holds"), paragraph(value("Keys"))),
      links("Machines", value("Machines")),
      links("Docs", value("Docs")),
      connections(id),
      value("Shot") && shotView(screens, value("Shot")),
      links("See", value("See")),
      links("Opens", value("Opens")),
    ]);
  }

  function inline(markdown) {
    const span = el("span");
    paintInline(span, markdown, path);
    return span;
  }

  function links(heading, value) {
    const list = linksOf(value ?? "");
    if (!list.length) return null;
    return el(
      "section",
      null,
      el("h3", null, heading),
      el(
        "ul",
        null,
        list.map((l) => {
          const to = route(path, l.href);
          return el(
            "li",
            null,
            el(
              "a",
              {
                href: to?.href ?? l.href,
                target: to?.external ? "_blank" : null,
                rel: to?.external ? "noreferrer" : null,
              },
              l.label,
            ),
          );
        }),
      ),
    );
  }

  function connections(id) {
    const { nodes, edges } = page.mermaid;
    const label = (nid) => plain(nodes.find((n) => n.id === nid)?.label ?? nid);
    const rows = [];
    for (const e of edges) {
      if (e.from !== id && e.to !== id) continue;
      const other = e.from === id ? e.to : e.from;
      const arrow = e.both
        ? "↔"
        : e.from === id
          ? e.handedIn
            ? "⇢"
            : "→"
          : e.handedIn
            ? "⇠"
            : "←";
      rows.push(
        el(
          "li",
          null,
          `${arrow} `,
          el(
            "button",
            { type: "button", class: "link-button", onclick: () => choose(other) },
            label(other),
          ),
          el("div", { class: "edge-label" }, e.label),
        ),
      );
    }
    return rows.length
      ? el("section", null, el("h3", null, "Arrows"), el("ul", { class: "edges" }, rows))
      : null;
  }

  drawn();
  select(null);

  return {
    select(id) {
      if (id !== selected) select(id);
    },
    dispose() {
      root.unmount();
    },
  };
}
