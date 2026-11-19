# atlas internals

How the viewer and server work, for changing them. The rules an edit must keep are in
[AGENTS.md](../AGENTS.md); adopting the engine and the config are in [README.md](../README.md).

## The viewer

- `index.html` is the only page. It holds no content and no colours: the server (`server.mjs`)
  hands it the project's config at `atlas.config.mjs` and every repo file at `repo/<path>`. A path
  that reaches the viewer from the address bar goes through `fetchRepoEntry`, which checks the URL
  the browser will request, not the path string; the server then serves only what git tracks.
- No build step; ES modules in `js/`. `pages.js` parses a page and has no DOM and no Node APIs, so
  `check.mjs` and the viewer read pages the same way: change the format there, in `check.mjs`, and in
  the project's README together. `config.js` is the project's config as the viewer uses it (the one place
  that imports it). `markdown.js` renders Markdown and Mermaid and turns every link into a `#` route (or
  a GitHub URL when the dev server wouldn't show the file); `files.js` paints what the doc view shows for a
  path (Markdown, a directory listing, an image, or text as numbered lines); `app.js` is the router (nav,
  history, the Read | Map toggle, the full-window doc view); `map.js` is the Map view of a level page
  (React Flow; `layout.js` places the boxes and `routes.js` draws the arrows and places their labels,
  both without DOM); `journeys.js` is the journeys; `shell.js` is the DOM helper, theme and fetching.
- **Routes** are the URL hash: `#<level>[/<box>]`, `#flows/<flow>` (a flow, under Journeys), `#machines`,
  `#dependencies`, `#journeys[/<journey>[/<step>]]`, `#doc/<encoded path>[/<fragment>]`. A route is a history
  entry, except choosing a box or a journey step. `#doc/` opens any repo path full window over the page:
  Markdown rendered (the fragment is a heading id), a directory as its tracked entries, an image, any other
  text with line numbers (`L12` highlights a line). Back (the button or the browser's) steps back through the
  docs and ends on the page and box the reader came from, with the map's zoom and the Read scroll as they were.
  `history.state.docs` counts the docs opened since; Escape and × close them all.
- **Read | Map** is a per-reader choice kept in `localStorage`. Read is the page as Markdown; a click
  on a diagram box scrolls to its `##` section. Map is `map.js`: the intro and a "How to read this" the
  viewer supplies sit above the diagram; a group opens its child page. It does not draw the page's
  Mermaid: it draws the parsed nodes, arrows and note links with React Flow, boxes sized by their
  text. `layout.js` puts the numbered path on one row in step order, left to right (a box the path
  leaves and doesn't go on from, or comes straight back from, is a spur beside it), wraps the row
  only when it can't be drawn at `READABLE_ZOOM`, and puts every other box and note in bands above
  and below, near what it connects to. Arrows along the row run straight, skip forward over it and
  back under it. A label never covers a box or another label: a side arrow's label is left out
  where there's no room (the panel lists every arrow), and choosing a box shows its own. Fit never
  zooms below `READABLE_ZOOM` (box text 13px and 11px on screen); a level that doesn't fit, as on a
  phone, opens at its start to pan. Boxes drag and the arrows follow; positions go to
  `localStorage` per page, only when a drag ends, and a page whose boxes aren't all saved is laid out
  afresh. Read view draws the Mermaid block itself.
- A flow's participants are clickable (`resolveParticipant` in `pages.js`, shared with the check): they open the box on the map (they set the view to Map).
- The nav is the README's `## The pages` list plus the entries the config's `nav` names. Every other
  level page is reached by a box's `Opens`; `loadLevelPages` in `pages.js` builds the set and each page's
  breadcrumb trail, and the viewer and `check.mjs` both call it.
- `styles/page.css` holds no colour: it paints with `--map-*` roles. The config's `tokens.roles` maps each
  role to a token of the project; `tokens.mjs` serves them at `tokens.css` as `--map-<role>: var(<token>)`,
  after the token files' blocks. `check.mjs` fails a raw colour here, a role the page or the scripts use that
  the config doesn't map, and a mapping to a token the files don't define. `--map-muted`, `--map-ink-subtle`
  and `--map-warning-tint` are mixed from roles in `page.css`.
- **Screens** (`screens.js`): the config's `screens` manifest is fetched once at start (`loadScreens`; none if
  the config has none; a manifest that doesn't load or parse is logged to the console and each `Shot` shows a
  "Screenshot unavailable" note in its place, not a blank). `shotCrop` is a CSS background crop of a region (percentages, so it scales with its
  holder), used under a box's section in Read view, in the Map panel and in a journey step card; `shotView` is
  the panel's full screen with each region outlined, numbered and linked to its `map` box, the pointer or focus
  lighting one. `resolveShot` in `pages.js` is shared with the check. Boxes on the Map stay text-only: a
  thumbnail would change `layout.js`'s box sizes.
- A dotted arrow (`handedIn` in `pages.js`) is drawn with the `is-handed-in` class (dashed); `check.mjs`'s
  `arrows.imports` leaves it out and holds the solid ones between code boxes to a value import: an import
  (type-only ones excluded) that reaches a file under the to box's source. `imports.mjs` resolves a workspace
  package specifier through `package.json` `exports` (else `main`) and follows `export ... from` lines by
  the names imported, so an import reaches the file that defines a name, not every file a barrel lists (`export *` passes a name on only from a module that has it, and a cycle of them ends);
  `reached` on each import is that list. A code box with no source under its Paths (none at all, or
  only a reference box's `Opens`) fails its solid arrows: it needs Paths, or the arrow is dotted. There is no inheritance
  from an opened page, since a page also holds boxes for its neighbours.
- The theme toggle sets the config's `tokens.dark` attribute on `<html>`; with no choice pinned it
  follows the system. Read colours from `<html>` (`markdown.js` does, for Mermaid), not from an element
  lower down, so the `--map-*` roles have resolved in the current theme.
- Third-party scripts are pinned with integrity hashes: React, ReactDOM, `@xyflow/react` and
  `marked` in `index.html`, Mermaid in `js/markdown.js`. To bump one, fetch the new file and
  recompute its `sha384`. React stays on 18 (19 has no UMD build); `@xyflow/react`'s UMD build wants a
  `jsxRuntime` global, which `js/jsx-runtime.js` maps onto React; `vendor/` holds its stylesheet.

## The server

`server.mjs` is one function, `createAtlasServer(configFile)`, behind both `vite-plugin.mjs` and
`serve.mjs`. Repo files are served under `repo/` only if `git ls-files` lists them (new unignored files in
the pages directory too, so a page opens before it is added); the list is re-read every two seconds. Text goes out as
`text/plain` (Markdown as Markdown, CSS as CSS) with `nosniff` and a `sandbox` CSP, never as HTML or SVG;
binary files are refused; a symlink must point at a file that would be served. `serveSource: false` in the
config narrows it to the pages directory and the config's `docs` globs (the check then requires the screens
manifest and its images to match them).
