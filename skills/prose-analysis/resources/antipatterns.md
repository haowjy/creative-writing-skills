# AI Writing Antipatterns

Patterns that distinguish AI-generated prose from human-written prose. Organized by evidence quality so you know what to trust.

## Research-Backed Signals

These patterns have been identified in peer-reviewed studies with measurable effect sizes. They're worth investigating when you spot them, though none are proof in isolation.

**Sources:** Kobak et al. (2024), BEA 2025 shared task, Ghostbuster (NAACL 2024), RAID (ACL 2024), Nature HSSCOMMS (2025).

### Lower lexical variability
AI text tends to reuse a narrower working vocabulary than human text of comparable length and genre. Measurable via MATTR (Moving Average Type-Token Ratio) or similar windowed metrics. Raw TTR is unreliable at varying text lengths.

### Fewer personal pronouns
AI-generated fiction uses fewer first-person and second-person pronouns relative to total word count. The prose reads as more "reported" than "experienced." Check the pronoun distribution output from `analyze.sh` — if a first-person chapter has unusually low I/me/my counts, investigate.

### More positive-emotion language
AI text skews toward positive sentiment, even in scenes that should be neutral or negative. This manifests as:
- Characters processing grief with remarkable resilience
- Dark situations described with silver-lining framing
- Emotional reactions that resolve too cleanly within the same paragraph

### Shallow character interiority
Characters think in summary rather than in the messy, associative way real thoughts work. Internal monologue reads like a narrator describing thoughts rather than a character having them. Signs:
- Thoughts are always grammatically complete and logically ordered
- No intrusive/unwanted thoughts, no tangents, no mid-thought corrections
- Emotional states are named rather than experienced ("I felt a surge of determination")

### Low dialogue subtext
Characters say what they mean directly. Subtext — the gap between what's said and what's meant — is rare. Conversations are efficient rather than realistic. Signs:
- Characters articulate their feelings clearly in dialogue
- Disagreements are stated rather than shown through evasion, topic-changing, or body language
- No conversations where the real subject is never mentioned

## Community-Identified Structural Patterns

These patterns are widely recognized by writers and editors who work with AI output. They haven't been formally studied with controlled experiments, but they're consistent enough across models and prompting approaches to be useful investigation triggers.

### "Clean but hollow" prose
Grammatically polished, rhythmically smooth, but lacking the irregularity that gives prose texture. Every sentence is competent. None are surprising. The prose is correct rather than alive.

### Generic arc progression
Scenes follow a predictable emotional trajectory: setup → complication → moment of doubt → resolution with growth. Real scenes often end unresolved, escalate without payoff, or achieve resolution in unexpected dimensions.

### Repetitive emotional choreography
Characters perform the same physical expressions of emotion: breath catching, jaw clenching, stomach dropping, heart hammering. The same metaphor clusters appear across different emotional contexts. Check `analyze.sh` repetition output — if the same physical action words cluster across paragraphs, investigate.

### Tidy-summary endings
Scenes and chapters end with a paragraph that summarizes the emotional meaning of what just happened. "As I watched the sunset, I realized that..." or "For the first time, I understood that..." Real prose more often ends on action, image, or dialogue — letting the reader draw the conclusion.

### Overused metaphor clusters
Certain metaphor domains recur across AI-generated text regardless of prompting: weight/heaviness for emotional burden, light/dark for knowledge/ignorance, water/drowning for being overwhelmed. Individual uses are fine — the pattern is in the frequency and predictability.

## Not Reliable: Word-Level "Slop Lists"

Lists of specific words claimed to indicate AI authorship (delve, tapestry, testament, nuanced, etc.) are **not reliable detection signals.** They are:

- Model-version dependent — word frequencies shift with each model update
- Prompt-dependent — style instructions dramatically change vocabulary
- Genre-confounded — "delve" appears in plenty of human-written academic and fantasy prose
- Near-random for Claude specifically — word-level heuristics trained on GPT output don't transfer

These lists are useful as editorial taste preferences ("I don't want my prose to sound like this") but not as evidence that text is AI-generated. If you're using them, be honest that it's a style choice, not a detection method.
