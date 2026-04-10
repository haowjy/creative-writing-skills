# Researchers

Agents that gather external context via web search and project exploration. Research is high-throughput information gathering — spawn multiple in parallel when exploring different dimensions.

## researcher

Web research via search and fetch. The orchestrator specifies a focus area in the prompt — this tells the researcher what lens to apply.

### Research Focus Areas

**craft** — Narrative technique and published craft knowledge. How do published authors handle unreliable narrators? What are best practices for multi-POV transitions? What do craft books say about pacing in middle-grade fantasy? Use when the writing team needs technique guidance beyond what the project's style files cover.

**world** — Real-world references for worldbuilding. Historical parallels, scientific accuracy, cultural context, geography. Use when the story's world mechanics draw from real-world systems — economics, biology, martial arts, regional culture — and the team needs grounding beyond what's in the wiki.

**genre** — Conventions, reader expectations, tropes, market context. What do readers of this genre expect from a training arc? How do successful isekai stories handle the knowledge-advantage trope? Use when making structural choices that should be informed by genre awareness — not to follow conventions blindly, but to know what you're subverting.

**sensitivity** — Representation, authenticity, community perspectives, common pitfalls. How do affected communities feel about this portrayal? What are common mistakes when writing this experience? Use when the story touches identity, disability, cultural practices, or traumatic experiences — early in the process, not as a last-minute check.

**fact-check** — Verifying specific claims. Dates, locations, technical details, real-world accuracy of fictional parallels. Use when the story makes specific factual claims that could be wrong and would undermine credibility.

### Choosing Focus Areas

Most research tasks have a clear primary focus. When the question spans multiple areas ("how should a martial arts tournament arc work?"), spawn multiple researchers in parallel: one for craft (tournament arc structure in fiction), one for world (real martial arts tournament formats), one for genre (tournament arcs in the specific genre).

Research reports are the deliverable — thorough, with trade-off analysis and source URLs. The orchestrator synthesizes across reports; the researcher goes deep on one dimension.

## explorer

Fast, cheap local content reading. Navigates the project's files and knowledge graph to gather context before more expensive agents run. Also mines past sessions for historical context via `meridian session`.

Use the explorer when:
- An orchestrator needs to understand what exists before composing a team
- A writer needs continuity anchors identified before drafting
- The knowledge graph needs to be consulted to find related content
- Past sessions need to be searched for relevant decisions or context

The explorer is cheap — use it liberally for orientation before committing to expensive spawns.
