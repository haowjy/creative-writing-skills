# Diagrams

Load when rendering relationships, flows, or connected views.

Use consistent names and visual identities across diagrams and accompanying
text. Label connections whose meanings differ, and show direction only when
the relationship has one.

HTML/SVG allows precise custom composition; Mermaid expresses standard diagrams
compactly. [React Flow](react-flow.md) supports connected React components and
selection coordinated with surrounding content.

For large diagrams, frame the relevant region initially. Group or separate
views when that clarifies the structure; add pan/zoom when shrinking would
make labels unreadable. Keep connections distinguishable where they cross
or enter groups. A diagram inside a collapsed or hidden container can lay out
at zero size; render or fit it when the container opens.

When selection reveals detail, retain enough surrounding context to show where
the item belongs. Make selectable diagram elements keyboard-accessible and
provide a textual account of the essential relationships.

Validate the Mermaid source as Markdown or `.mmd` (`/md-validation`); passing
the containing HTML file to that checker can skip its diagrams. Then inspect
labels, connection endpoints,
clipping, and readability at the delivered size. Syntax validation cannot
catch an incorrect or misleading relationship.
