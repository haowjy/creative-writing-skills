/* What both viewers share: DOM helper, theme, page fetching, and the top bar. */
import { DARK, storageKey } from "./config.js";
import { parsePage } from "./pages.js";

/** Where the dev server serves the repo's files, relative to index.html. */
const REPO_ROOT = "repo/";

/** el("a", { href, class }, child, ...): children are nodes or strings; false/null are skipped. */
export function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs ?? {})) {
    if (value == null || value === false) continue;
    if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value === true ? "" : value);
  }
  node.append(...children.flat().filter((c) => c != null && c !== false));
  return node;
}

// ---- The side panel: the reader sets its width and hides it; both are kept in this browser ----

const PANEL_KEY = storageKey("panel");
const PANEL_WIDTH = 360;
const panelState = { width: PANEL_WIDTH, hidden: false };
try {
  const saved = JSON.parse(localStorage.getItem(PANEL_KEY)) ?? {};
  if (Number.isFinite(saved.width)) panelState.width = saved.width;
  panelState.hidden = saved.hidden === true;
} catch {
  // No storage: the default width, shown.
}
/** Lays out the workspace on screen now, or null when the view has no panel. */
let layPanel = null;

function setPanel(change) {
  Object.assign(panelState, change);
  try {
    localStorage.setItem(PANEL_KEY, JSON.stringify(panelState));
  } catch {
    // Not remembered; it still holds for this visit.
  }
  syncPanelButton();
  layPanel?.();
}

/** The top bar's button that hides and shows the panel. The app hides it on a view without one. */
export const panelButton = el("button", {
  type: "button",
  class: "icon-button panel-button",
  "aria-label": "Hide details",
  title: "Hide details",
  onclick: () => setPanel({ hidden: !panelState.hidden }),
});
function syncPanelButton() {
  const hidden = panelState.hidden;
  panelButton.textContent = "◧";
  panelButton.setAttribute("aria-label", hidden ? "Show details" : "Hide details");
  panelButton.title = hidden ? "Show details" : "Hide details";
  panelButton.setAttribute("aria-expanded", String(!hidden));
}
syncPanelButton();

/** Shows the panel if the reader hid it: they picked something whose detail is in it. */
export function showPanel() {
  if (panelState.hidden) setPanel({ hidden: false });
}

/**
 * Gives the workspace `host` the width the reader chose for its `panel`, and an edge to drag: the
 * edge resizes the panel, a double-click resets it, and the arrow keys move it. On a narrow screen
 * the panel sits under the diagram and none of this applies.
 */
export function adjustablePanel(host, panel) {
  const wide = matchMedia("(min-width: 720px)");
  const grip = el("div", {
    class: "panel-grip",
    role: "separator",
    tabindex: "0",
    "aria-orientation": "vertical",
    "aria-label": "Resize the details panel",
    title: "Drag to resize; double-click to reset",
  });
  host.append(grip);

  // The panel keeps a readable width, and the diagram keeps room beside it.
  const fit = (w) => Math.round(Math.max(240, Math.min(w, 900, host.clientWidth - 320)));
  function lay() {
    const on = wide.matches;
    const shown = panelState.hidden ? 0 : fit(panelState.width);
    host.style.gridTemplateColumns = on ? `minmax(0, 1fr) ${shown}px` : "";
    panel.hidden = on && panelState.hidden;
    grip.hidden = !on || panelState.hidden;
    grip.style.right = `${shown - 4}px`;
    grip.setAttribute("aria-valuenow", String(shown));
  }

  grip.addEventListener("pointerdown", (event) => {
    event.preventDefault();
    grip.setPointerCapture(event.pointerId);
    host.classList.add("resizing");
  });
  grip.addEventListener("pointermove", (event) => {
    if (!grip.hasPointerCapture(event.pointerId)) return;
    // Laid out, not saved, on each move: the drop saves.
    panelState.width = fit(host.getBoundingClientRect().right - event.clientX);
    lay();
  });
  const drop = () => {
    host.classList.remove("resizing");
    setPanel({});
  };
  grip.addEventListener("pointerup", drop);
  grip.addEventListener("pointercancel", drop);
  grip.addEventListener("dblclick", () => setPanel({ width: PANEL_WIDTH }));
  grip.addEventListener("keydown", (event) => {
    const step = { ArrowLeft: 16, ArrowRight: -16 }[event.key];
    if (!step) return;
    event.preventDefault();
    setPanel({ width: fit(fit(panelState.width) + step) });
  });
  const follow = () => lay();
  wide.addEventListener("change", follow);
  addEventListener("resize", follow);
  layPanel = follow;
  lay();
  return () => {
    wide.removeEventListener("change", follow);
    removeEventListener("resize", follow);
    if (layPanel === follow) layPanel = null;
  };
}

/**
 * A repo path as the dev server answers it: { kind: "dir", entries: [{ name, dir }] },
 * { kind: "image", url }, or { kind: "text", text }.
 */
export async function fetchRepoEntry(path) {
  const root = new URL(REPO_ROOT, location.href);
  const url = new URL(REPO_ROOT + path.split("/").map(encodeURIComponent).join("/"), location.href);
  // `path` can come from the address bar (#doc/). Check the URL the browser will request, not
  // the string: URL parsing turns %2e%2e into .. and moves a ? tail into the query.
  const requested = url.pathname.startsWith(root.pathname)
    ? decodeURIComponent(url.pathname.slice(root.pathname.length))
    : null;
  if (url.origin !== root.origin || url.search || url.hash || requested !== path) {
    throw new Error(`${path}: not a file in this repository`);
  }
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${path}: ${response.status} ${response.statusText}`.trim());
  const type = response.headers.get("content-type") ?? "";
  if (type.startsWith("application/json")) return { kind: "dir", entries: await response.json() };
  if (type.startsWith("image/")) return { kind: "image", url: url.href };
  return { kind: "text", text: await response.text() };
}

/** Where the dev server serves a repo file (an image's `src`). */
export const repoUrl = (path) =>
  new URL(REPO_ROOT + path.split("/").map(encodeURIComponent).join("/"), location.href).href;

/** A repo file's text. */
export async function fetchRepoFile(path) {
  const entry = await fetchRepoEntry(path);
  if (entry.kind !== "text") throw new Error(`${path}: not a text file`);
  return entry.text;
}

export const fetchPage = async (path) => parsePage(await fetchRepoFile(path));

// ---- Theme: follows the system until the reader pins one ----

const THEME_KEY = storageKey("theme");
const themeListeners = new Set();
const systemDark = matchMedia("(prefers-color-scheme: dark)");
let pinned = null;
export const currentTheme = () => pinned ?? (systemDark.matches ? "dark" : "light");

/** Puts <html> in the theme: the token files' dark attribute on or off. */
function applyTheme() {
  const html = document.documentElement;
  const dark = currentTheme() === "dark";
  if (dark) html.setAttribute(DARK.attribute, DARK.value);
  else html.removeAttribute(DARK.attribute);
  html.style.colorScheme = dark ? "dark" : "light";
  for (const cb of themeListeners) cb();
}

try {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === "light" || saved === "dark") pinned = saved;
} catch {
  // No storage: follow the system.
}
applyTheme();
systemDark.addEventListener("change", applyTheme);

export const onThemeChange = (cb) => themeListeners.add(cb);

export function pinTheme(theme) {
  pinned = theme;
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    // Not remembered; the pin still holds for this visit.
  }
  applyTheme();
}
