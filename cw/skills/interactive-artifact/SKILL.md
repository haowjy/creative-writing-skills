---
name: interactive-artifact
description: |
  Build a self-contained HTML file that makes structured information explorable through
  interaction — clicking, filtering, sorting, expanding. Default to Mermaid diagrams;
  choose a different interaction pattern when the data calls for it.
disable-model-invocation: true
---

# Interactive Artifact

A single HTML file that opens in a browser. The viewer clicks, filters, or expands to
explore — not just read.

## Principles

- **One view, detail on demand.** Show the full picture. Clicking an element reveals
  detail in a collapsible sidebar — don't split information across pages or tabs.
- **Maximize the content area.** Fill the viewport (`height: 100vh`, flex column).
  Navigation and detail are collapsible sidebars with width transitions, not fixed
  headers or overlays. Content area gets all remaining space.
- **Light mode default with toggle.** Drive colors from CSS custom properties. Toggle
  dark mode by adding `.dark` to `<html>`. Include a ☀/🌙 button in the toolbar.
- **Static, no build step.** CDN `<script>` tags. One HTML file, no npm, no bundler.
- **Works on a phone.** Responsive layout, touch pan/pinch-zoom, tap targets ≥ 44px.

`resources/layout-and-theme.md` has the concrete layout, theme, and mobile patterns
shared across all interaction patterns.

## Interaction patterns

Default to **Mermaid diagrams** when information has relationships or flow. Pick a
different pattern when the data is better served by it:

| Pattern | When to use | Resource |
|---|---|---|
| Explorable diagram | Dependencies, flow, system maps | `resources/explorable-diagram.md` |
| Data table | Records with sortable/filterable columns | `resources/data-table.md` |
| Data chart | Quantities, trends, distributions | `resources/data-chart.md` |
| Timeline | Chronological events with detail | `resources/timeline.md` |
| Tree / TOC | Hierarchy navigation, document outline | `resources/tree-and-toc.md` |
| Card grid | Items with summary + expandable detail | `resources/card-grid.md` |
| Diff / comparison | Before/after, version diff | `resources/diff-view.md` |

For custom node rendering, drag, or live filtering on graphs beyond what Mermaid
offers, see `resources/experimental-react-flow.md`.
