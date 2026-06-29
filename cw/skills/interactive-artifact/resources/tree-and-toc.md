# Tree and TOC

Expandable hierarchy or document outline. No library needed — native HTML handles
both patterns.

## Tree (File Explorer Style)

Use `<details>` and `<summary>` for expand/collapse. Render recursively from data.

```html
<input id="treeSearch" placeholder="Filter...">
<div id="tree"></div>
<script>
const data = {
  name: "root", children: [
    { name: "docs", children: [{ name: "releasing.md" }, { name: "arch.md" }] },
    { name: "src", children: [{ name: "cli.py" }, { name: "config.py" }] },
  ],
};

function renderNode(n) {
  if (!n.children) return `<li class="leaf">${n.name}</li>`;
  return `<li><details open><summary>${n.name}</summary><ul>${
    n.children.map(renderNode).join("")
  }</ul></details></li>`;
}

document.getElementById("tree").innerHTML = `<ul>${renderNode(data)}</ul>`;

document.getElementById("treeSearch").oninput = e => {
  const q = e.target.value.toLowerCase();
  document.querySelectorAll("#tree li").forEach(li => {
    li.style.display = li.textContent.toLowerCase().includes(q) ? "" : "none";
  });
};
</script>
```

Click a leaf to show detail — add a click handler on `.leaf` elements.

## TOC (Document Outline)

Generate a nav from headings. Use `IntersectionObserver` to highlight the active
section.

```html
<style>html { scroll-behavior: smooth } #toc a.active { font-weight: bold }</style>
<nav id="toc"></nav>
<main id="doc"><!-- headings with ids --></main>
<script>
const headings = [...document.querySelectorAll("#doc h2, #doc h3")];
document.getElementById("toc").innerHTML = headings
  .map(h => `<a href="#${h.id}" data-id="${h.id}">${h.textContent}</a><br>`)
  .join("");

const links = [...document.querySelectorAll("#toc a")];
const obs = new IntersectionObserver(entries => {
  entries.filter(e => e.isIntersecting).forEach(e => {
    links.forEach(a => a.classList.toggle("active", a.dataset.id === e.target.id));
  });
}, { rootMargin: "-20% 0px -70% 0px" });
headings.forEach(h => obs.observe(h));
</script>
```
