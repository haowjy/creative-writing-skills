# Diagram Craft

Use consistent names and visual identities across diagrams and accompanying
text. Label connections whose meanings differ, and show direction only when
the relationship has one.

Keep a connection's label to a few words. A label that needs a sentence collides with its
neighbours: put a short name on the connection and the sentence in a table under the diagram
(connection, when it happens). This matters most in state diagrams, where labels crowd around
each state.

Mermaid expresses standard diagrams compactly. HTML or SVG allows precise custom composition, and
[React Flow](react-flow.md) supports connected React components and selection
coordinated with surrounding content.

For large diagrams, frame the relevant region initially. Group or separate
views when that clarifies the structure; add pan/zoom when shrinking would
make labels unreadable. Keep connections distinguishable where they cross
or enter groups. A diagram inside a collapsed or hidden container can lay out
at zero size; render or fit it when the container opens.

When selection reveals detail, retain enough surrounding context to show where
the item belongs. Make selectable diagram elements keyboard-accessible and
provide a textual account of the essential relationships.

Validate the Mermaid source as Markdown or `.mmd` (`/creative-writing-skills:md-validation`); passing
the containing HTML file to that checker can skip its diagrams. Then inspect
labels, connection endpoints,
clipping, and readability at the delivered size. Syntax validation cannot
catch an incorrect or misleading relationship.
