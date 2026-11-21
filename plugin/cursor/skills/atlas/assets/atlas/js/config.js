/*
 * The project's atlas.config.mjs as the viewer uses it. The dev server serves the config at
 * `atlas.config.mjs` beside index.html, whatever it is called on disk.
 */
import config from "../atlas.config.mjs";
import { DEFAULT_DARK, globRegExp } from "./pages.js";

export const TITLE = config.title;
export const MAP_DIR = config.pagesDir;
export const NAV = config.nav ?? {};
/** Documents listed in the top-bar Docs menu. */
export const DOCUMENTS = config.documents ?? [];
/** The screens manifest's repo path, or null when the project has none. */
export const SCREENS = config.screens ?? null;
export const STATE_MACHINES_INDEX = config.stateMachines?.index ?? null;
export const DEPENDENCIES_PAGE = config.nav?.dependencies
  ? `${MAP_DIR}/${config.dependencies.page}`
  : null;
/** The attribute and value the token files put the dark theme under. */
export const DARK = config.tokens?.dark ?? DEFAULT_DARK;

/** The key the viewer files a browser setting under, so two maps on one origin don't share settings. */
export const storageKey = (name) => `atlas:${config.repo}:${name}`;

/** A repo path on GitHub. */
export const sourceUrl = (path) =>
  `https://github.com/${config.repo}/blob/${config.branch}/${path}`;

const docs = (config.docs ?? []).map(globRegExp);

/** Whether the dev server shows this repo path in the viewer (see `serveSource` in the config). */
export const opensLocally = (path) =>
  config.serveSource !== false ||
  path.startsWith(`${MAP_DIR}/`) ||
  docs.some((re) => re.test(path));
