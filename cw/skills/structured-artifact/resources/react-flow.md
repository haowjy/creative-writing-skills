# React Flow

Load when using React Flow for connected custom components or an explorable
node graph.

Use `nodeTypes` for custom React nodes and handles for their connection points.
Nodes can contain text, images, mockups, or code excerpts. Choose each node's
contents and shape for the information it represents.

Coordinate selection with surrounding explanatory text through shared state.
Give the canvas an explicit size, import the library stylesheet, and fit the
initial view to the relevant content. Automatic graph layout requires a
separate layout choice.

React Flow enables node dragging, connecting, and Backspace deletion by
default. Unless readers need to edit, set `nodesDraggable={false}`,
`nodesConnectable={false}`, and `deleteKeyCode={null}`; keep selection,
keyboard focus, pan, and zoom where they help readers explore.

Use the current `@xyflow/react` [custom-node documentation](https://reactflow.dev/learn/customization/custom-nodes)
and [layout guidance](https://reactflow.dev/learn/layouting/layouting). Deliver
static output as described in [delivery](delivery.md).
