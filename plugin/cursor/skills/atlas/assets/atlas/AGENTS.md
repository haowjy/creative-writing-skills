# Atlas engine

A viewer and a check for a project's atlas pages. The pages and the config are the
project's; this directory holds no content and names no project. [README.md](README.md) says how
to adopt it and lists the config; [example/](example/) is a working toy.

- This directory's source is the `/creative-writing-skills:atlas` skill in meridian-base: a project copies it unchanged,
  and the check fails when an installed skill's copy differs. Fix the engine there.
- Keep it free of project names: nothing here outside comments may name the project it is used in,
  its directories or its packages (the project's own paths belong in its `atlas.config.mjs`).
- `pages.js` parses a page and has no DOM and no Node APIs, so `check.mjs` and the viewer read
  pages the same way. Change the page format there, in `check.mjs` and in the README together. A
  Mermaid `subgraph` is called a frame in code and reader-facing messages; `group` remains only a
  box kind, never the React Flow node type for a frame.
- `index.html` and `styles/page.css` hold no content and no colours: `page.css` paints with `--map-*`
  roles only, which the config's `tokens.roles` maps to the project's tokens (a few are mixed from
  those in `page.css`). Where the page needs a colour no role gives, add a role to the README's list and
  to every config (`example/` too); `check.mjs` fails a raw colour here and an unmapped role.
- Read colours from `<html>`, not an element lower down, so the `--map-*` roles have resolved in
  the current theme.
- A repo path from the address bar goes through `fetchRepoEntry`, which checks the URL the browser
  will request. The server serves only what git tracks, as `text/plain` with `nosniff` and a
  `sandbox` CSP, never as HTML or SVG; don't widen that.
- Third-party scripts are pinned with integrity hashes. To bump one, fetch the new file and
  recompute its `sha384`. React stays on 18 (19 has no UMD build).
- Expandable content must overlay what is already there rather than changing neighbouring geometry;
  this includes the top-bar Docs menu. Arrows and labels come from the router in `routes.js`, which keeps every
  arrow clear of boxes, frame titles and borders and every label on its own arrow, free of everything; a
  dragged frame must not visually enclose an unrelated box. Only an intentional reader-controlled split, such as the details panel, may resize its neighbour.
  A frame is derived from its member boxes whenever the map is drawn, not saved as independent layout.

A page may carry its own box positions as `%% at <id> <x> <y>` lines in its Mermaid block (parsed in
`pages.js`, checked in `check.mjs`, applied by `layout.js` before any automatic placement, written by the
Legend's "Copy box positions" through `positionLines`). A box without one is placed around the placed
ones, never over them. The opening view is the Fit view, so no box starts under an overlay.

Run `node --test` in this directory after a change to `routes.js`, `route-grid.js`, `frames.js` or
`layout.js`: `test/routes.test.mjs` is what "a correct route" means and fails on any page of `example/` or of
the atlas in `ATLAS_CONFIG` (when set or present). Add a property to the test before relying on it.

How the viewer, routes, Map layout and server work: [`.context/CONTEXT.md`](.context/CONTEXT.md).
