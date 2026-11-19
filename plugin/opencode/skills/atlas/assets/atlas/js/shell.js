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
