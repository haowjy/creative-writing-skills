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
  (React Flow; `layout.js` places the boxes, `frames.js` is the frames' geometry, and `routes.js` with
  `route-grid.js` draws the arrows and places their labels, all without DOM); `journeys.js` is the journeys; `shell.js` is the DOM helper, theme and fetching.
- **Routes** are the URL hash: `#<level>[/<box>]`, `#flows/<flow>` (a flow, under Journeys), `#machines`,
  `#dependencies`, `#journeys[/<journey>[/<step>]]`, `#doc/<encoded path>[/<fragment>]`. A route is a history
  entry, except choosing a box or a journey step. `#doc/` opens any repo path full window over the page:
  Markdown rendered (the fragment is a heading id), a directory as its tracked entries, an image, any other
  text with line numbers (`L12` highlights a line). Back (the button or the browser's) steps back through the
  docs and ends on the page and box the reader came from, with the map's zoom and the Read scroll as they were.
  `history.state.docs` counts the docs opened since; Escape and × close them all.
- **Read | Map** is a per-reader choice kept in `localStorage`. Read is the page as Markdown; a click
  on a diagram box scrolls to its `##` section. Map is `map.js`: it draws the parsed nodes, arrows,
  notes and labelled structural frames with React Flow, boxes sized by their text. The page title and
  description live in the details panel; the reading hint and stacked-box page-opening marker are
  named in the legend. The breadcrumb takes no row: on the map it floats over the top-left corner, in Read it is the
  first line of the article. Expandable content overlays what is already there. `layout.js` uses a deterministic numbered path: frames are ordered
  by where the path first enters them, their members form sensible grids with arrow-aware gaps,
  branch frames sit beside the spine, and outside boxes sit beside the unit they connect to. The spine wraps before it becomes too
  wide for readable zoom. A frame is computed from its members every render, so it follows a drag or
  saved positions. `routes.js` routes every arrow again after a drag (see Arrow routing). The opening view and the Fit button are the same view (`fitLevel`): the whole level, labels included, sits clear of every overlay (top bar buttons, breadcrumb, zoom buttons, legend; `freeArea` in `map.js` reads their rectangles, so any window size and an opened legend count). A small window therefore opens at a low zoom and the reader zooms in; a readable opening zoom was dropped because it put boxes under the overlays.
  **Authored positions:** a page's `%% at <id> <x> <y>` lines (`parsePage` → `mermaid.positions`) reach `layoutLevel` as `level.authored`; `withAuthored` keeps them and puts each unplaced box at the automatic layout's place if that is clear (AUTHORED_GAP round placed boxes, no frame outline enclosing a non-member), else at the nearest clear spot to its linked or frame-mate boxes. The reader's saved drags (`localStorage`) still win when every box has one; Reset layout clears them and lays out again, so it returns to the page's positions. The Legend's "Copy box positions" writes the boxes' current positions with `positionLines` (shifted to start at 0, 0, rounded). It is in the Legend, which already overlays, because it is rare and a toolbar button would not be. If a dragged frame would enclose a non-member, its outline breaks into member outlines instead. The top bar's Docs menu overlays the page and opens configured documents in the reading view. Opening a page and going up animate a zoom when motion is allowed;
  Escape goes up to the parent. Boxes drag and the arrows follow; positions go to `localStorage` per
  page, only when a drag ends, and a page whose boxes aren't all saved is laid out afresh. Read view
  draws the Mermaid block itself. A level may put `- View: <kind>` before its Mermaid block; the value is shown beside the title and changes no map behavior.
- A flow's participants are clickable (`resolveParticipant` in `pages.js`, shared with the check): they open the box on the map (they set the view to Map).
- The nav is the README's `## The pages` list plus the entries the config's `nav` names. When `documents` is configured, Docs is an overlay menu beside that nav. Every other
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

## Arrow routing

`routes.js` (arrows, labels) and `route-grid.js` (grid and search) turn boxes, frames and arrows into
polylines, as plain data with no DOM; `routeLevel` adapts a page. Orthogonal connector routing in the
manner of libavoid (Wybrow, Marriott and Stuckey, "Orthogonal connector routing"), written here
because the engine loads no bundled code and libavoid is LGPL C++/WebAssembly; JointJS's manhattan
router, a grid A*, has the same search but no separation, which is why it overlaps shared lanes.

- Nodes sit every 8 px (wider on a huge drawing) at absolute multiples of the pitch. A node is free
  unless it lies inside a box inflated by `CLEAR` (12 px), a frame title inflated by `FRAME_CLEAR`
  (8), or an earlier label. Horizontal moves are refused within `FRAME_CLEAR` of a frame's
  horizontal border, vertical ones near a vertical border, so a border is crossed squarely and
  never run along. An arrow's own two boxes are open only in the strip straight out of each side
  (the stub): the way out and in is perpendicular, ports are the lanes of that strip, clear of the
  corners.
- A* over (node, direction): cost is length, 40 per bend, a surcharge for crossing an arrow (more for
  a numbered one) or a frame border, nearness to boxes (so lanes centre in a gap) and an adjacent
  occupied lane. A route can only step on free nodes, so it keeps the clearances with no repair pass.
- Arrows go one at a time, the numbered path first, then shortest first. A routed arrow holds its
  nodes: a later arrow may cross it but never shares a lane or bends on it, so parallel arrows are at
  least one pitch apart, and ports on a side spread without a rule for it.
- An arrow is committed with a label: a straight run of its route where the label rect keeps `CLEAR` from
  boxes and touches no title, border, other label or other arrow. With none, the route is rebuilt to
  pass through a run of its own: candidate runs, nearest the direct way first, each routed to and from. A candidate whose route would double back over its own nodes (a port off the run's line) is skipped.
  The label then holds its rectangle against later arrows. Routes do not change when a box is selected;
  the viewer only hides the labels of unselected boxes' arrows.
- An arrow that finds no route, or no label place (a crowded box walled in by earlier arrows and
  labels), is routed again first, up to five passes; the best pass stands. Boxes drawn over each other
  have no route: the arrow is a straight line and `exact` is false.
- Spacing is layout's job: frames stand 26 px (40 above) off their members and boxes in a frame are
  34 px apart (`frames.js`, `layout.js`), enough for one lane between.
- `test/routes.test.mjs` is the definition of correct (properties in its header), run on every page of the
  example atlas and a project atlas (`ATLAS_CONFIG`) laid out and with each box dragged, and on seeded random cases.
  Not guaranteed: a box with more arrows than its sides have lanes, many labels in a small area, boxes
  overlapping. The test generates no case with more than two arrows per box on average.

## The server

`server.mjs` is one function, `createAtlasServer(configFile)`, behind both `vite-plugin.mjs` and
`serve.mjs`. Repo files are served under `repo/` only if `git ls-files` lists them (new unignored files in
the pages directory too, so a page opens before it is added); the list is re-read every two seconds. Text goes out as
`text/plain` (Markdown as Markdown, CSS as CSS) with `nosniff` and a `sandbox` CSP, never as HTML or SVG;
binary files are refused; a symlink must point at a file that would be served. `serveSource: false` in the
config narrows it to the pages directory and the config's `docs` globs (the check then requires the screens
manifest and its images to match them).
