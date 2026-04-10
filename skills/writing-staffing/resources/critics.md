# Critics

Critics catch what revision can't — voice drift, structural issues, continuity holes. The value of multiple critics comes from different focus areas, not redundant reads of the same concern.

## critic

Adversarial draft review with a specified focus area. Give each critic a different focus area so you get breadth — the content itself tells you what perspectives matter. Read-only.

### Focus Areas

**structure** — Plot logic, pacing, scene necessity, stakes, setup/payoff. Does every scene earn its place? Do stakes escalate or plateau? Are promises set up that get paid off? Does the pacing serve the emotional arc or fight it? Use on any draft, but especially on chapters that bridge between high-intensity scenes where pacing sag is most likely.

**character** — Motivation coherence, arc progression, relationship dynamics. Do characters act from established motivation or convenience? Are relationship shifts earned through interaction, not narrated? Does the character's internal state match their behavior? Use when characters make significant choices, confront each other, or change.

**voice** — Dialogue quality, POV consistency, subtext, voice drift. Does each character sound distinct? Does the narrator's voice stay consistent? Is there subtext in dialogue or is everything surface-level? Does the prose drift toward generic AI voice or maintain the project's established style? Use on every draft — voice is the most common casualty of AI-assisted writing.

**prose** — Line-level quality: rhythm, clarity, repetition, show vs tell. Are sentences varied or monotonous? Is language precise or vague? Does the prose show states through action or tell them through narration? Are there echoed words or phrases? Use when prose polish matters — pivotal scenes, published chapters.

**continuity** — Facts, timeline, geography, character state. Does this chapter contradict established canon? Are characters in the right place? Does the timeline hold? Is information the character knows consistent with what they've experienced? Use on any draft, but critical for chapters that reference events from earlier in the story.

### Choosing Focus Areas

The content tells you what perspectives matter. A battle scene needs structure (pacing) and continuity (established abilities) more than prose polish. A quiet character scene needs character (motivation) and voice (dialogue quality) more than structure. A chapter that spans multiple locations needs continuity above all.

For standard chapters, three critics with different focus areas provides good coverage. For pivotal scenes, expand to four or five and consider duplicating the most critical focus area.

### Fan-Out for Coverage

The multi-agent role decomposition pattern this skill advocates is empirically supported. HoLLMwood (2024, Findings of EMNLP, https://aclanthology.org/2024.findings-emnlp.474/) found that splitting creative writing across distinct writer/editor/actor roles produced measurable improvements in coherence, relevance, interestingness, and overall quality over strong single-agent baselines. The critic fan-out pattern this skill advocates is the critique half of that empirically-supported architecture. If you're reading this and wondering whether the fan-out overhead is worth it, that's the evidence: the overhead pays for itself in finding quality.

When fanning out, use the best available model and vary focus areas across critics so the panel covers different dimensions:

```
meridian spawn -a critic -p "Focus: structure" -f $DRAFT
meridian spawn -a critic -p "Focus: continuity" -f $DRAFT $CANON
meridian spawn -a critic -p "Focus: voice" -f $DRAFT $VOICE_STYLE
```

For pivotal scenes where a focus area really matters, duplicate that focus across two different agent spawns rather than relying on a single pass.

## continuity-checker

Cross-references content for contradictions across the full project. Unlike the critic's continuity focus (which compares one draft against provided context), the continuity-checker navigates the project's knowledge graph and `$MERIDIAN_FS_DIR/` to find what *should* be cross-referenced. Read-only.

Use the continuity-checker when:
- A chapter references events, locations, or character state from significantly earlier in the story
- Multiple chapters are being drafted in parallel and need to stay consistent
- The story spans enough time or complexity that the critic's provided context isn't sufficient
- After timeline or world-building changes that might invalidate earlier content

The continuity-checker is more expensive than a critic with continuity focus — it reads broadly. Use the critic for routine continuity checks and the continuity-checker for deep cross-project validation.
