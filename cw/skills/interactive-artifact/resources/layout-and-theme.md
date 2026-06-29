# Layout and Theme

Shared patterns for all interactive artifacts. Load this alongside the pattern-specific
resource.

## CDN Base Stack

```html
<script src="https://cdn.tailwindcss.com"></script>
<script type="module">
  import { codeToHtml } from 'https://esm.sh/shiki@1';
  window.codeToHtml = codeToHtml;
</script>
```

Tailwind's CDN build warns in console; ignore for static artifacts. Shiki is only
needed if the artifact shows syntax-highlighted code in detail panels.

## Viewport-Filling Layout

The artifact fills the browser window. The content area gets all space not used by
a toolbar.

```html
<body style="display:flex;flex-direction:column;height:100vh;overflow:hidden;margin:0">
  <header><!-- toolbar: title, theme toggle, nav buttons --></header>
  <main style="display:flex;flex:1;min-height:0;gap:1rem;padding:1rem">
    <!-- optional left sidebar -->
    <section style="flex:1;min-width:0;overflow:hidden">
      <!-- primary content area -->
    </section>
    <!-- optional right sidebar -->
  </main>
</body>
```

`min-height: 0` on `<main>` prevents flex children from overflowing. The content
section takes all remaining space.

## Collapsible Sidebars

Sidebars are flex children with a width transition. Collapsing sets width to 0;
a fixed-width inner wrapper prevents content reflow during animation.

```html
<div id="detail-panel" class="sidebar collapsed">
  <div class="sidebar-inner" style="width:360px">
    <!-- detail content here -->
  </div>
</div>
```

```css
.sidebar {
  flex-shrink: 0;
  overflow: hidden;
  transition: width 0.2s ease;
}
.sidebar.collapsed { width: 0; }
.sidebar:not(.collapsed) { width: 360px; }
.sidebar-inner { height: 100%; overflow-y: auto; }
```

```js
function toggleDetail() {
  document.getElementById('detail-panel').classList.toggle('collapsed');
}
```

Use a left sidebar for navigation (~300px) and a right sidebar for detail (~360px).
Both start collapsed. Open the detail sidebar when the viewer clicks an element.

## Theme

Drive all colors from CSS custom properties. Default to light; toggle with a class
on `<html>`.

```css
:root {
  --bg: #ffffff; --surface: #f5f5f5; --text: #1a1a1a;
  --muted: #6b7280; --line: #e5e7eb; --accent: #2563eb;
}
.dark {
  --bg: #1a1a1a; --surface: #262626; --text: #e5e5e5;
  --muted: #9ca3af; --line: #404040; --accent: #60a5fa;
}
body { background: var(--bg); color: var(--text); }
```

```js
function toggleTheme() {
  document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme',
    document.documentElement.classList.contains('dark') ? 'dark' : 'light');
}
if (localStorage.getItem('theme') === 'dark') {
  document.documentElement.classList.add('dark');
}
```

When using Mermaid, re-initialize with the matching theme after toggle — see
`explorable-diagram.md`.

## Mobile

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

Render the detail panel as a bottom sheet on narrow screens. A Tailwind breakpoint
(`md:`) on the sidebar covers both layouts. Keep tap targets ≥ 44px.

## Serve Over Tailscale (optional)

View the artifact on another device by serving over your tailnet. Only offer if
Tailscale is present: `command -v tailscale`.

```bash
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("",0)); print(s.getsockname()[1]); s.close()')
python3 -m http.server "$PORT" &
tailscale serve --bg "$PORT"
```

Proxies HTTPS on your tailnet to `localhost:$PORT`. Tear down with
`tailscale serve --bg "$PORT" off`.
