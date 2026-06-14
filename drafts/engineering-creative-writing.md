# Engineering Creative Writing — working draft

> Scratch location. Move to your personal site repo when ready. This file holds:
> the locked decisions, the opening draft, the full outline, the receipts/anchors
> (so nothing gets lost in chat), and a brainstorm of alternate directions.

---

## Decisions (locked)

- **Venue:** long-form blog essay, canonical on the personal site. Reddit teaser cut later. X for distribution (full post on the owned site; thread/excerpt on X driving back).
- **Audience:** writers who use AI — technically curious, not devs. Translate every SWE term into writer language.
- **Goal:** teach the mental model first (that's what earns trust), soft-pitch the skills at the end.
- **Strategic frame:** this post is top-of-funnel that advertises *the founder*, not a product. It demonstrates the same agentic-writing runtime that powers **Voluma** (scientific agents + collaborative paper editing), through the one lens people actually want to read about — fiction. The fiction is the trojan horse for the science platform. The writing work is the R&D sandbox + content engine; Voluma is the single commercial bet.

---

## Opening (draft v1 — voice probe)

> **Engineering Creative Writing**
>
> About a year ago I posted a set of creative-writing skills, back when Anthropic
> first shipped Agent Skills. They were simple — I'd basically taken my own writing
> workflow and split it into a few shareable files. Someone in the comments asked me
> a fair question: *how is this any different from just keeping a folder of prompts
> you paste in?*
>
> I gave him a paragraph. It wasn't wrong, but it was the answer of someone who'd
> stumbled into something he didn't fully understand yet.
>
> Since then I mostly stopped writing — and went deep on something that turned out to
> be the same problem in disguise: how do you actually build good software with an AI?
> A year of that, and I came back to the writing skills with answers I didn't have
> before. They've evolved a lot. More importantly, I finally understand *why* the
> original ones worked at all.
>
> So this is the real answer to that comment. Not "skills vs. a prompt folder" — but
> the whole thing underneath it: how these models actually think, where they keep
> their memory, and why almost everything about getting good writing out of them comes
> down to one idea — **keeping the model's mind clear.** Everything else hangs off that.

---

## Outline (locked)

1. **Open on the question the thread left hanging** — the prompt-folder question; half an answer then, the real answer now; a year of building software with AI in between.
2. **What an LLM is** — a knowledgeable mind with no body, no cerebellum, no instincts, no sense of time. Everything follows from this.
3. **The models have personalities (and they've drifted)** — Claude's constitution → morals + reads hidden intent (fading in 4.7/4.8); GPT 5.2+ literal, instruction-locked (great at code, stiffer at prose). One concrete example each.
4. **The three memories** — training data (now RL/code-skewed, quietly starves writing) → context window (working memory + its levels) → external memory: the wiki (Karpathy anchor) → progressive disclosure.
5. **The hinge: keep the mind clear** — "too much info degrades output" (my v1 line), now with its mechanism. Pasta-conversation vs. battle-scene.

*— the payoff: "keep the mind clear" cashed out four ways —*

6. **Skills = progressive disclosure of *craft*** — what the model should DO, pulled in only when relevant. v1 callbacks: Claude-specific → everywhere; the MCP aside; no copy-paste.
7. **The wiki = progressive disclosure of *knowledge*** — the compounding, self-maintaining story bible that kills continuity errors. Karpathy ↔ my chronicler / continuity-checker / kb-maintainer.
8. **Subagents = focus past one mind** — a novel won't fit in one clear context, so spawn focused specialists; the coordinator holds the book. Writers'-room translation.
9. **Multiple models = a real panel, not clones** — different minds, non-overlapping blind spots; beats a model grading its own agreeable homework. Doubles as the "nerfed for writing" workaround (cheap models for prose, expensive for judgment). Repo fan-out as proof.
10. **How to run it** — Claude Pro project on-ramp → local filesystem for the real thing; pokemon-amber as the worked example.
11. **Honest close** — still not fully sold on AI prose; style files moved the needle; it's all terminal today; building a real site → soft pitch the repo.

### The unifying frame (the spine of 6–9)

|  | What the model should **DO** | What the model should **KNOW** |
|---|---|---|
| **Mechanism** | Skills (progressive disclosure of *craft*) | The wiki/kb (progressive disclosure of *facts*) |
| **Failure if crowded** | loses focus → **subagents** | loses independence → **multiple models** |

Four ideas, one principle.

---

## Receipts & anchors (do not lose)

- **LLM-wiki priority.** First commit carrying the wiki concept: `069ab68` "creative writing skill(s)", **2025-10-25**. By v0.0.3 (**2025-10-30**), `cw-official-docs/SKILL.md` stated the rule **"Wiki pages contain ONLY confirmed information"** — the canonical-knowledge discipline. Karpathy's `llm-wiki` gist was **created 2026-04-04** (~5 months later; ~5k stars in days). Both timestamps public. Footnote-ready.
- **The reader avatar.** v1 thread: mod (YoavYariv) asked "how is a skill better than a prompt bank?" and, separately, "I use FILES to store prompts — should I try skills?" The thread trailed off **without fully answering him.** v2 = the answer, written to that person.
- **v1 callbacks** (earned-evolution beats): "skills are pretty specific to Claude" → now industry-standard everywhere; "they could be MCPs but don't need that"; "I'm still not the most confident in AI's ability to write prose."
- **Repo as proof.** `muse` spawns `critic` + `reader-sim`; those fan out across `opus / gpt / deepseek / sonnet`. Karpathy's wiki ops map to: ingest → `chronicler`, query → `continuity-checker`, lint → `kb-maintainer`.

---

## Brainstorm: additional directions & alternate structures

### The biggest missing asset: concrete prose examples
The notes already flag `[maybe find some examples?]`. Nothing sells "keep the mind clear" like **showing** it: the *same scene* generated three ways — (a) naive one-shot prompt, (b) bloated context stuffed with irrelevant history, (c) the focused-system version. Readers feel the difference instantly. This single addition would do more for credibility than any amount of theory. Strong candidate to weave through the whole piece rather than sit in one section.

### Centerpiece-metaphor option: "a mind without a body"
Expand the throwaway line into the spine. No cerebellum (no instinct, no felt sense of pacing in the gut). No proprioception. No sense of time. No persistent self between sessions. Each absence has a *writing consequence* — and "giving it a body" becomes the through-line: style files give it a voice, the wiki gives it memory, character-sim gives it a self to inhabit. Could reframe sections 6–9 as "the prosthetics."

### Elevate character-sim
Right now it's a sub-point. It might be the single most novel and charming idea you have — "the agent goes through the scene *as* the character." Consider promoting it to a named centerpiece (it's the most shareable concept on X). It's also the cleanest example of "giving the mind a body."

### Spicy-but-original section: "why coding ate the writing"
The RL-environment / correctness-bias argument — thousands of startups feeding coding tasks into training, biasing models toward *getting it right* over *ambiguity*, quietly degrading prose. Few people frame it this way. High-share potential, but needs to be argued carefully (it's a claim, not a fact). Pair with the "nerfed for writing → use cheaper/alt models" practical payoff.

### The sycophancy beat
"The AI just tells me it's good" is a universal writer complaint. Give the agreeable-reviewer problem its own short beat — it's the emotional hook that makes "multiple models" land. A model grading its own homework is structurally incapable of the critique you need.

### Structural fork: one post or two?
This is a *lot*. Real option to split:
- **Post A — "How LLMs actually think" (the mental model):** sections 1–5. Evergreen, reference-able, wide appeal.
- **Post B — "Engineering Creative Writing" (the payoff):** sections 6–11, demonstrating the system.
Splitting de-risks length, gives you two shots at distribution, and seeds the *series*. Counter-argument: the payoff is what makes the mental model worth reading — splitting buries the lede. Decide deliberately.

### Series / spin-off candidates (you wanted a content plan)
1. **This post** (lead — widest appeal, the Karpathy hook, human interest).
2. **"The LLM Wiki, five months before it had a name"** — the priority story + how to build a story bible. The hook is strong enough to stand alone.
3. **meridian-cli** — the orchestration layer; how you actually run multi-agent writing. (Devs-only; post #2–3, not the lead.)
4. **"Character Simulation"** — deep dive on the most novel technique.
5. **"Cheap models write better prose than the expensive ones"** — the economics/nerfed-for-writing piece.
6. **Voluma origin (later)** — same engine, pointed at science. Connects the body of work.
Frame the series as *facets of one worldview* — an engineer applying real software principles to creative work — not random project writeups. Ship one, learn, ship the next.

### Format / medium ideas
- Embed the README mermaid diagram (muse → subagents flow) as the one visual.
- A "same scene, three contexts" side-by-side block.
- Pre-write pull-quotes for X: the priority line ("five months before it had a name"), "subagents that are all the same model are clones," "a knowledgeable mind with no body."

### Risks to watch
- **Model-personality claims** are the best hook *and* the flame bait — anchor each to one example, soften "autistic" → "literal-minded / instruction-locked."
- **Length / jargon creep** for a non-dev audience.
- **Don't let it read as a product ad** — ideas first, tool second; the soft pitch only earns its place after the teaching.
