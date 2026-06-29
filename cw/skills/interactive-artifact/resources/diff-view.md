# Diff / Comparison

Side-by-side or unified diff view with syntax highlighting. Use for before/after
comparisons, version diffs, or change review.

## Library

**Diff2Html** for rendering + **jsdiff** for computing diffs from strings.
Diff2Html ~335 KB gzipped (with syntax highlighting), jsdiff ~8 KB gzipped.

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/diff2html@3.4.56/bundles/css/diff2html.min.css">
<script src="https://cdn.jsdelivr.net/npm/diff@8.0.2/dist/diff.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/diff2html@3.4.56/bundles/js/diff2html-ui.min.js"></script>
```

If you already have a unified diff string, omit jsdiff.

## Minimal Example

```html
<div>
  <button onclick="renderDiff('side-by-side')">Side by Side</button>
  <button onclick="renderDiff('line-by-line')">Unified</button>
</div>
<div id="diff"></div>
<script>
const oldText = "function greet(name) {\n  return 'Hello ' + name;\n}\n";
const newText = "function greet(name) {\n  return `Hello ${name}!`;\n}\n";
const patch = Diff.createTwoFilesPatch("old.js", "new.js", oldText, newText);

function renderDiff(mode) {
  const el = document.getElementById("diff");
  el.innerHTML = "";
  const ui = new Diff2HtmlUI(el, patch, {
    drawFileList: false,
    outputFormat: mode,
    matching: "lines",
    highlight: true,
  });
  ui.draw();
  ui.highlightCode();
}

renderDiff("side-by-side");
</script>
```

## Plain DOM Alternative

For a simple two-column text comparison without syntax highlighting, two `<pre>`
elements side by side with highlighted lines is less code than loading Diff2Html.
