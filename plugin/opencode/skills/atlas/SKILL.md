---
name: atlas
description: 'Load when the human wants a map they click down through, of anything with parts and relationships (a codebase, a design not built yet, a story''s cast): Markdown pages with one Mermaid diagram each, and the viewer and check this skill carries. Its `resources/diagrams.md` holds diagram craft for any page.'
metadata:
  type: reference
---

# Atlas

An atlas is a set of Markdown pages, one Mermaid diagram each, that a reader
explores from the top down: an overview, then a page for each part that has
parts of its own. The diagrams are what the reader looks at; the words are
detail one click away. Each page reads on its own on GitHub or in an editor,
so the pages are the one source, and agents edit them like any other doc.
The engine in `assets/atlas/` draws them and checks them. For one diagram
on a page that isn't an atlas, open `resources/diagrams.md` instead; the
rest of this skill is for building an atlas.

## Draw Each Page

- **One diagram, about ten boxes.** Draw the relationships the reader
  follows, not every link that exists: a diagram with every import or every
  acquaintance on it is unreadable. What doesn't fit goes in a box's section
  or a child page.
- **A name and a one-line role on every box**, in the reader's words, so the
  diagram reads without the panel.
- **Arrows say what flows or binds**, in a few words ("claims the run", "owes
  a debt to"). Where a page has a main path (a request, a scan, a plot
  line), number its arrows in order; the rest are side paths.
- **A part with parts of its own opens its own page.** The index lists the
  top-level pages side by side; anything else is reached by clicking the box
  that holds it, so no part gets a section of the index to itself.
- **A box's section** starts with one sentence, which the panel shows; the
  rest of the section and of the page is the depth, for whoever opens it.
- **Images**: crop a screenshot or illustration to what the box covers, and
  let the engine spotlight the region. The explanation goes in the page, not
  on the image.

## Build It

Copy `assets/atlas/` into the project as `tools/atlas/`, unchanged, and
follow its `README.md`, which holds the page format, the config and what the
check catches; `example/` is a working toy. A change to the engine goes to
this skill's source in meridian-base, not to `.mars/` or the project's copy:
sync rewrites `.mars/`, and the check fails when the copy differs from it.
To move a project's own older copy (such as `tools/architecture-map/`),
replace it with this one, update every reference to it (scripts, the dev
server's plugin, the viewer's URL, docs), and rewrite the project's rule for
where engine changes go.

Serve it (`node tools/atlas/serve.mjs <config>`) and look at every page in a
browser, at desktop and phone width: a label that collides, a page whose
diagram you can't take in at a glance, a box whose role doesn't read without
the panel. Run the check and fix the pages until it passes.

## Keep It True

Change the pages in the same commit as what they describe, and say so in
the project's `AGENTS.md`, beside the check in the project's gate. The check
catches pages that break apart, and for a codebase, pages that drift from
the code; it is a tripwire, not a proof. Whether each word and arrow is
still true is yours to read.

For craft the page format leaves to you (framing a large diagram, labels,
keyboard access), open `resources/diagrams.md`.
