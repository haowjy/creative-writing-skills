---
name: writing-principles
description: What fiction readers actually want, framed as four composable reward channels (transportation, aesthetic, social simulation, flow), and the specific documented ways alignment training damages each one. Grounded in reader-psychology research and empirical NLP findings. Load when drafting prose, critiquing a draft, deciding whether to show or tell, diagnosing why a passage feels flat, or reasoning about why a scene is or isn't working.
---

# Writing Principles

Fiction is a composite reward experience. Readers don't enjoy a story through a single mechanism — they enjoy it through at least four separable but composable reward channels, each with its own research literature. Good prose protects all four at once; damaging any one damages the reading experience.

This skill names the four channels so you know what the prose is protecting, then names the specific failure modes alignment training produces against each channel so you know what you are calibrating against, then points at the craft tradition that converged on the same picture. The positive prescription comes first because a diagnosis without a target produces prose that resists its training but has nothing to aim for.

---

# Part 1: The four reward channels

Reader enjoyment is not a single variable. Research across cognitive science, literary theory, and media psychology identifies at least four separable reward channels that compose the experience of reading fiction.

**Transportation / absorption.** Readers mentally enter a story world and become less aware of their immediate environment. Strongest empirical support of the four — a meta-analysis of 132 effect sizes establishes this as a measurable construct with reliable antecedents and consequences (van Laer et al. 2014, [doi:10.1086/673383](https://doi.org/10.1086/673383)). Reading-specific flow research confirms absorption as distinct from attention and positively linked to reading pleasure (Thissen et al. 2018, [doi:10.3389/fpsyg.2018.02542](https://doi.org/10.3389/fpsyg.2018.02542)). Protected by coherent narrative progression, consistent POV, concrete sensory grounding, and minimal unearned confusion.

**Aesthetic / stylistic pleasure.** Literary language, foregrounding, distinctive voice, and form are intrinsically rewarding — independent of plot and character. Narrativity and literariness shift readers toward an aesthetic attitude, and style and suspense rely on different processing routes (Wimmer et al. 2023; van Peer et al. 2007; Hartung et al. 2021). Style is a separate reward channel, not decoration. Protected by sentence-level variety, rhythm, specific word choices that reward attention, and sentence shapes that do work.

**Social simulation / character modeling.** Readers model fictional characters as minds with motives, feelings, and perspective. Modestly supported — a meta-analysis found a small positive effect of fiction on social cognition (Dodell-Feder & Tamir 2018, [doi:10.1037/xge0000395](https://doi.org/10.1037/xge0000395)). Caveat: the famous Kidd & Castano claim that literary fiction immediately improves theory of mind has failed preregistered replication (Panero et al. 2016). Treat social simulation as a real engagement mechanism, not a proven real-world cognitive effect. Protected by character access through concrete behavior and interiority, distinct voices per character, and emotion the reader has to interpret rather than being told.

**Flow / challenge-fit.** Reading pleasure peaks when the text is challenging enough to engage attention but not so hard that fluency breaks — an inverted-U relationship (Thissen et al. 2018). Flow is a real construct in reading, separate from both transportation and aesthetic reward. Protected by readable challenge, pacing that matches the scene's work, and sentences that support rather than obstruct comprehension.

## The channels compose; they do not compete

Readers want all four at once. A skill that optimizes only for withholding or inference damages the other three: over-explaining breaks social simulation, under-explaining breaks transportation, generic style breaks aesthetic pleasure, impenetrable style breaks flow. Good prose is **calibration across channels**, not a single "withhold more" rule.

## Fiction is not special because it is untrue

An important reframe before the diagnosis: when the same short story was labeled fictional versus factual, readers showed no meaningful difference in immersion, appreciation, or reading time (Hartung et al. 2017, [pubmed 28983269](https://pubmed.ncbi.nlm.nih.gov/28983269/)). Fiction works because the reader adopts a *simulation stance* and the text invites and rewards that stance — not because it withholds or disclaims factuality.

This matters because it blocks the cargo-cult reading of "show don't tell" where the rule becomes "never explain anything." Fiction is not the opposite of exposition. It is prose that earns and maintains a particular reader stance. Some scenes maintain the stance through dense interiority, some through clean orientation, some through information delivered via a character's attention. The stance is the thing. Withholding is one tool for protecting it, not the goal.

---

# Part 2: Your training has specific failure modes against each channel

Alignment training and chat-template formatting measurably reduce surface diversity and increase determinism in creative generation. This is empirically documented in recent NLP research, not folklore. The honest framing is narrower than "RLHF kills fiction" — alignment changes the tradeoff surface, and naive reward optimization is a poor proxy for literary quality.

The generalized root cause is **the helpfulness instinct**: training rewarded explaining clearly, delivering complete information, resolving ambiguity, and correcting misunderstanding. Fiction is anti-helpful at precise moments — subtext should not be stated, foreshadowing should not connect immediately to its payoff, unreliable narrators should not be corrected, dramatic irony requires withholding, mysteries require telegraphing the solution only at the right moment. The failure modes below are the specific surface expressions of that instinct, organized by the channel each one damages most.

For per-pattern deep dives with before/after examples, fix heuristics, and the common traps (including how "show don't tell" produces its own stock-gesture failure mode), read [`resources/failure-modes.md`](resources/failure-modes.md).

## Damage to the aesthetic channel

**Syntactic templating.** The model reaches for the same sentence structures repeatedly. Templates are copied directly from pretraining data, and fine-tuning and alignment do *not* overwrite them (Shaib et al. 2024 EMNLP, [aclanthology.org/2024.emnlp-main.368](https://aclanthology.org/2024.emnlp-main.368/)). Output often feels rhythmically identical across different content.

**Attractor-state fluency.** RLHF-aligned models show lower token entropy and form attractor patterns that reduce creative variation. Prose feels "smoothed" rather than "written" ("Creativity Has Left the Chat," [arxiv 2406.05587](https://arxiv.org/abs/2406.05587)).

**Lower uncertainty than human writers.** Instruction-tuned and reasoning models have measurably lower token-level uncertainty than base models and than human professional writers, with the gap *larger* in creative writing than in functional domains ([arxiv 2602.16162](https://arxiv.org/abs/2602.16162)). Every sentence picks the expected word; distinctive character voices flatten into the same measured register.

**Chat-template diversity collapse.** The structure of chat templates itself suppresses topical and semantic diversity on creative tasks, independent of content. Explicitly instructing the model to "be creative" does not close the gap ("The Price of Format: Diversity Collapse in LLMs," [aclanthology.org/2025.findings-emnlp.836](https://aclanthology.org/2025.findings-emnlp.836/)). This one is not fully fixable from the prompt side; mitigate with looser prompt shapes rather than louder instructions.

## Damage to social simulation

**Labeled emotions.** "She felt sad." "A sense of dread settled over him." The cleanest and most efficient way to communicate a state is to name it, and the helpfulness instinct prefers clarity. Labels collapse the reader's modeling work — the reader was going to reconstruct the feeling from behavior, and that reconstruction was the reward.

**Stock physical tells.** When the model tries to apply "show don't tell" without specificity, it reaches for templated gestures: clenched fists, shaky breaths, averted eyes, tightening jaws. These are the failure mode of show-don't-tell itself — signifiers without specificity, produced because the training recognizes the form of showing but not the function. A specific action reveals; a stock gesture rubber-stamps.

**Homogenized voices.** Every character inherits the model's default articulate, emotionally fluent register. Inarticulate characters, emotionally avoidant characters, characters who think in fragments — these are outside the training distribution. Voice variety *is* characterization; without it, readers cannot build distinct mental models of the cast.

**Collapsed ambiguity.** The narrator explains what the character doesn't know, resolves motivations the scene was leaving open, tips morally uncertain moments toward a verdict. Ambiguity reads as communication failure to the training signal, so the instinct is to repair it.

## Damage to transportation

**Middle-drift consistency bugs.** In long-form narratives, factual and temporal errors cluster in the *middle* of narratives, not at openings or endings ("Lost in Stories," [arxiv 2603.05890](https://arxiv.org/abs/2603.05890)). Openings receive attention; endings receive convergent pressure; middles drift. Attend to continuity more carefully in the middle of long sequences than at the start or end.

**POV drift and authorial intrusion.** The narrator slips registers, breaks the close-third illusion, addresses the reader directly, or starts narrating from outside the POV character's head. The reader was inside one mind; now they're reading a report.

**Info-dumping.** Exposition blocks pause the story to teach: "The danger rating system classifies areas from Tier 1 to Tier 5..." The reader was inside the story; now they are in a mini-lecture. Worldbuilding that bypasses the POV character's attention breaks the dream.

## Damage to flow

**Over-elaboration.** Every beat gets its full articulation. Emotional moments receive proportionally weighty prose — "my heart ached with the profound emptiness of your absence" where "I miss you" would land harder. The prose performs feeling at the reader rather than trusting the moment to land.

**Scope inflation.** The confrontation gets its aftermath, plus a reflection scene, plus a teaser. Training rewarded complete, thorough responses; leaving scope unresolved was penalized. The narrative's weight distribution flattens because every scene resolves itself.

**Dense exposition at the wrong moment.** Worldbuilding, backstory, or mechanics arriving in the middle of an action beat or an emotional peak. The pacing the scene needed collapses into explanation mode.

**Weak suspense generation.** LLMs are empirically unreliable for generating suspenseful stories; iterative planning helps ("Creating Suspenseful Stories," 2024 EACL, [aclanthology.org/2024.eacl-long.147](https://aclanthology.org/2024.eacl-long.147/)). Suspense requires sustained withholding against the helpfulness grain.

---

# Part 3: The craft tradition supports this frame

The four-channel picture is not a lab artifact. Serious craft writers across a century of craft writing have independently converged on the same structure, usually focusing on one channel at a time.

- **Transportation** is Gardner's "vivid and continuous dream" (*The Art of Fiction*, 1983) — the writer's job is to protect an unbroken imagined world against anything that would pull the reader out of it.
- **Social simulation** is Hemingway's iceberg (*Death in the Afternoon*, 1932, ch. 16 — "the writer may omit things that he knows"), Baxter's *The Art of Subtext* (2007), and Wood's partial perspective and free indirect style in *How Fiction Works* (2008). All three converge on: the reader reconstructing interior states from surface detail is where the reward lives.
- **Aesthetic** is Le Guin's "truthful selection" and her carrier-bag theory of fiction — pattern, rhythm, and relation as the craft's primary materials, not conflict mechanics.
- **The reader contract** is Saunders's "mutual assumption of intelligence" (*A Swim in a Pond in the Rain*, 2021) and Forster's claim that "the reader must sit down alone and struggle with the writer" (*Aspects of the Novel*, 1927). The reader is an active collaborator, not a target for delivered information.

What the naive "withholding is everything" reading of craft misses — and what the four-channel frame recovers — is that fiction also needs causal structure (Forster's "what happens next and why"), truthful selection over minimalism (Le Guin), and pattern at sentence, scene, and structural levels. "Show don't tell" is the rough shorthand for protecting social simulation and aesthetic channels simultaneously. It is a heuristic, not a law, and it breaks down wherever it damages transportation or flow.

---

# Part 4: Implications for how you draft

Behavioral heuristics, not a checklist.

- **Protect narrative coherence for transportation.** Keep POV consistent, keep physical geography stable, keep track of what characters know and when they learned it. Middle-drift is a documented failure mode for you — attend to continuity more carefully in the middle of long sequences than at the start or end.
- **Offer sentence-level variety for aesthetic reward.** The default register your training produces is competent and smooth. Resist it at moments that deserve texture. Vary sentence length and shape. Let voice do work. Match the project's established rhythm even in passages that feel generic to you.
- **Give character access through concrete behavior and interiority for social simulation.** When you feel the urge to label an emotion, ask whether a specific action — not a stock gesture — would let the reader model the state instead. When you feel the urge to explain a motivation, ask whether the ambiguity is the scene's work.
- **Provide readable challenge for flow.** Pacing should match the scene's work. Dense exposition in the middle of an emotional peak breaks flow; so does over-elaboration that drags a brief beat past its weight.
- **Notice the helpfulness instinct firing.** When you want to explain what you just showed, resolve the tension you just built, clarify the ambiguity you just created, label the emotion you just dramatized, deliver worldbuilding the character wouldn't narrate, add a reflection paragraph the scene didn't need, or smooth a distinctive voice into generic competence — that's the instinct. It is not always wrong. It is always worth asking which channel you are about to damage and whether the reader was going to do that work themselves.
- **"Show don't tell" is calibration, not law.** Show when the moment matters — emotional peaks, character-defining choices, relationship shifts. Tell when emotional texture doesn't matter — transitions, time compression, low-stakes connective tissue. The mistake isn't telling per se. It's telling during moments that deserved showing, or dramatizing moments that only needed brief summary.

---

# Part 5: What this skill is opinionated about

The four-channel frame is the diagnosis, and the diagnosis is research-backed. The documented failure modes of alignment training are empirically supported. These are the parts of this skill that should carry weight across projects.

The specific writing disciplines that follow — how much to show versus tell, how dense to make subtext, how much exposition to allow, how literary versus how plain the voice should be — are **project choices**. Craft tradition itself disagrees on these. Hemingway and Le Guin share a skeleton but produce very different prose; Saunders and Wood agree on the reader contract but diverge on how much narrator presence is acceptable. These stylistic questions belong in project-local style files, not in a general principles skill.

Use the four-channel frame and the documented failure modes as the baseline. Defer to project style files where they override. The skill has teeth on what is evidence-backed; it is deliberately neutral on stylistic questions where the evidence is weaker than the tradition of strong disagreement.

---

# Resources

- [`resources/failure-modes.md`](resources/failure-modes.md) — per-pattern deep dives (over-elaboration, flattened voice, info-dumping, labeled emotions and the stock-tells trap, resolved tension, homogenized voices, emotional commentary, collapsed ambiguity, over-intensified language, project-style mismatch) with examples and fix heuristics. Read when diagnosing a specific passage or when a draft feels off and you need to name what's wrong.
- [`resources/citations.md`](resources/citations.md) — full citation list for the reader-psychology research, NLP failure-mode research, and craft tradition references used in this skill. Read when you need to verify a claim or point another agent at the source.
