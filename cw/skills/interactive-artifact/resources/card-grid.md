# Card Grid

Items displayed as cards with summary info, filterable and sortable, click to
expand detail. No library needed — CSS Grid handles layout.

## Minimal Example

```html
<input id="cardSearch" placeholder="Search...">
<select id="cardSort">
  <option value="name">Name</option>
  <option value="score">Score</option>
</select>
<div id="cards" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px"></div>
<script>
const items = [
  { name: "Parser", type: "code", score: 8, detail: "Builds AST from source" },
  { name: "Release", type: "docs", score: 5, detail: "Ship process docs" },
];

function renderCards() {
  const q = document.getElementById("cardSearch").value.toLowerCase();
  const s = document.getElementById("cardSort").value;
  document.getElementById("cards").innerHTML = items
    .filter(x => JSON.stringify(x).toLowerCase().includes(q))
    .sort((a, b) => (a[s] > b[s] ? 1 : -1))
    .map(x => `<button class="card" onclick="showDetail('${x.name}')">
      <b>${x.name}</b><br><span style="color:var(--muted)">${x.type}</span>
    </button>`)
    .join("");
}

document.getElementById("cardSearch").oninput = renderCards;
document.getElementById("cardSort").onchange = renderCards;
renderCards();
</script>
```

For true masonry (variable-height packing), use `column-count` CSS or the Masonry
library (~7 KB gzip), but equal-height grid is usually sufficient.
