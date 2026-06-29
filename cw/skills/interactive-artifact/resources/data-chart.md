# Data Chart

Interactive chart with hover tooltips and click callbacks. Use for quantities,
trends, or distributions.

## Library

**Chart.js** — ~70 KB gzipped.

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"></script>
```

## Minimal Example

```html
<canvas id="chart" height="120"></canvas>
<script>
new Chart(document.getElementById("chart"), {
  type: "bar",  // bar, line, scatter, pie, doughnut, radar
  data: {
    labels: ["Docs", "Code", "Tests"],
    datasets: [{ label: "Items", data: [12, 19, 7] }],
  },
  options: {
    plugins: { tooltip: { enabled: true } },
    onClick: (evt, points) => {
      if (!points.length) return;
      showDetail(points[0].index);  // wire to detail panel
    },
  },
});
</script>
```

Supports bar, line, scatter, pie, doughnut, and radar out of the box.
