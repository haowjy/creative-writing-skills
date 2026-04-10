# Reader Simulation

Experiential reader-response agent. The `reader-sim` agent reads a draft as a reader, not as a critic, and reports the experience as it happens, structured by the four empirically-supported reader reward channels (transportation, aesthetic, social simulation, flow). It produces raw experiential data — the orchestrator or critic translates that data into craft findings.

## reader-sim

Stays in the reader stance throughout the read. Doesn't diagnose craft problems, doesn't propose fixes, doesn't rewrite passages. Its value is the felt experience of reading, reported with concrete textual anchors — "I skimmed the fourth paragraph of scene three" is the kind of signal the critic cannot generate from outside.

Read-only. Takes a draft file and (optionally) a focus spec or style references. Produces a structured experiential report. Cheap to spawn; you can run multiple reader-sim instances on the same draft when the draft is long or the stakes are high, because different perspectives land on different reading sensibilities.

## When to spawn

- **After a draft converges in the write/critique loop** — before presenting to the author, a reader-sim pass tells you what the text actually feels like to read, which is information the critic's pattern-matching doesn't capture.
- **On long drafts or pivotal scenes** — chapters where middle-drift consistency bugs are likely ("Lost in Stories," [arxiv 2603.05890](https://arxiv.org/abs/2603.05890)), or scenes where the author is uncertain whether the emotional target lands.
- **When craft critique and reader experience might diverge** — a scene can be technically clean and still leave a reader cold. A reader-sim pass is the cheapest way to notice that before the author does.
- **Alongside critics, not instead of them** — the two reports answer different questions. A critic catches what a reader might miss and vice versa; the orchestrator synthesizes across both.

## What reader-sim is not

Reader-sim is not a second critic. When its report reads like a craft critique — "the pacing is off" — the stance collapsed and the value is lost. The orchestrator should reject that kind of output and re-spawn with tighter framing.

Reader-sim is also not a summary agent. The caller already has the draft. What reader-sim provides is the experience of reading it.

## Fan-out patterns

For a long draft, one reader-sim pass is usually enough. For a pivotal scene, fan out two or three reader-sim instances so the orchestrator can see whether an experience (absorption, aesthetic reward, emotional landing) was robust across readers or specific to one perspective.

## Relationship to character-sim

Reader-sim and `character-sim` are symmetric simulation agents on different sides of the text. Character-sim *produces* in-character behavior from one side of the page; reader-sim *consumes* the finished text from the other side and reports what landed. Both report experience rather than craft findings, and both are read-only.
