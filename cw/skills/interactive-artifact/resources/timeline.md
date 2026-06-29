# Timeline

Chronological events on a zoomable, pannable axis with click-to-detail. Use for
event histories, release timelines, or project milestones.

## Library

**vis-timeline** — ~154 KB gzipped JS, ~4 KB CSS.

```html
<link href="https://cdn.jsdelivr.net/npm/vis-timeline@8.5.1/styles/vis-timeline-graph2d.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/vis-timeline@8.5.1/standalone/umd/vis-timeline-graph2d.min.js"></script>
```

## Minimal Example

```html
<div id="timeline" style="height:220px"></div>
<script>
const items = new vis.DataSet([
  { id: 1, content: "Kickoff", start: "2026-01-05" },
  { id: 2, content: "Prototype", start: "2026-02-12" },
  { id: 3, content: "Launch", start: "2026-04-01" },
]);

const timeline = new vis.Timeline(
  document.getElementById("timeline"),
  items,
  { zoomable: true, moveable: true }
);

timeline.on("select", e => {
  const item = items.get(e.items[0]);
  if (item) showDetail(item.id);  // wire to detail panel
});
</script>
```

Drag to pan, scroll to zoom. Group events by category with the `group` property.

## Plain DOM Alternative

For ≤10 static events, a styled `<ol>` with click handlers is simpler.
