# Experimental: React Flow

## CDN Stack

React Flow needs React, ReactDOM, and the library as UMD globals, plus its CSS.

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reactflow@11/dist/style.css">
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/reactflow@11/dist/umd/index.js"></script>
<script src="https://cdn.tailwindcss.com"></script>
```

## Minimal Graph

```js
const { useState, useCallback, createElement: h } = React;
const { default: ReactFlow, Background, Controls, applyNodeChanges } = window.ReactFlow;

const initialNodes = [
  { id: 'route',    position: { x: 0,   y: 0   }, data: { label: 'POST /orders' } },
  { id: 'orderSvc', position: { x: 0,   y: 120 }, data: { label: 'OrderService' } },
  { id: 'orderRepo',position: { x: 0,   y: 240 }, data: { label: 'orders table' } },
];
const initialEdges = [
  { id: 'e1', source: 'route',    target: 'orderSvc' },
  { id: 'e2', source: 'orderSvc', target: 'orderRepo' },
];

function App() {
  const [nodes, setNodes] = useState(initialNodes);
  const onNodesChange = useCallback(
    (c) => setNodes((n) => applyNodeChanges(c, n)), []);
  const onNodeClick = useCallback((_, node) => showDetail(node.id), []);

  return h(ReactFlow, {
    nodes, edges: initialEdges, onNodesChange, onNodeClick, fitView: true,
  }, h(Background), h(Controls));
}

ReactDOM.createRoot(document.getElementById('root')).render(h(App));
```

`onNodeClick` replaces Mermaid's click directives; the detail-panel pattern from
`html-patterns.md` works unchanged. Custom nodes go through React Flow's `nodeTypes` map
when you need richer rendering than a label.
