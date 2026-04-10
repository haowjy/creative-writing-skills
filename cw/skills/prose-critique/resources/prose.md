# Prose Review

Evaluate line-level quality — rhythm, clarity, word choice, repetition, and show vs tell.

## Rhythm

Read the prose aloud (mentally). Monotonous rhythm — every sentence the same length and structure — puts the reader to sleep regardless of content.

**Sentence length variation** — short sentences for impact, tension, and clarity. Longer sentences for reflection, complexity, and flow. The variation creates rhythm. A page of uniformly medium-length sentences is the prose equivalent of a monotone voice.

**Sentence opener variety** — if five consecutive sentences start with "She" or "He" or "The," the prose has a structural tic. Vary openers: action, dialogue, setting detail, interiority, dependent clauses.

**Paragraph rhythm** — paragraphs also have rhythm. A long paragraph followed by a short one creates emphasis. Several short paragraphs in sequence create urgency.

## Clarity

Can the reader follow what's happening? Prose can be lyrical and still be clear. Confusion is not depth.

**Action clarity** — in physical sequences (fights, chases, complex movement), can the reader picture what's happening? Unclear blocking is a common problem in action scenes.

**Pronoun confusion** — when multiple characters of the same gender are in a scene, pronoun references can become ambiguous. "She turned to her and told her she was wrong" — who is who?

**Temporal clarity** — is the timeline of events within a scene clear? Flashbacks, memories, and time jumps need clear signals.

**Causal clarity** — when something happens, can the reader tell why? Unclear cause-and-effect makes the reader work harder than they should on logistics instead of engaging with the story.

## Word Choice

**Precision** — "walked" vs "shuffled" vs "strode" vs "crept." Each carries specific meaning. Flag generic verbs where a specific one would do more work.

**Repetition** — the same distinctive word appearing twice in close proximity. "Said" can repeat endlessly; "luminous" appearing twice in a paragraph is noticeable. The more unusual the word, the more visible the repetition.

**Purple prose** — over-description that draws attention to itself. "The incandescent vermillion of the dying sun cast its resplendent effulgence across the obsidian surface of the tumultuous sea." If the prose is more interesting than the story, it's a problem.

**Filter words** — "she saw," "he heard," "she felt," "he noticed." These add distance between the reader and the experience. "She saw the door open" vs "The door opened." The filter word version tells the reader about the character's perception; the direct version puts the reader in the character's perception.

Not every filter word is wrong — sometimes you want to emphasize the act of perceiving. But habitual use weakens the prose.

## Show vs Tell

**Emotional telling** — labeling emotions instead of demonstrating them. "She was angry" vs showing anger through specific, character-revealing behavior. The showing version does more work because it reveals HOW this specific character expresses anger.

**Telling isn't always wrong.** Summary narration, transitions, low-stakes moments — these are appropriate places to tell rather than show. The problem is telling during moments that deserve dramatization: emotional peaks, character-defining choices, relationship shifts.

**The test:** is this moment important enough that the reader should experience it, or is it information the reader needs before the next important moment? Experience → show. Information → telling is fine.

## AI Prose Patterns

Patterns common in AI-generated fiction that a critic should flag:

**Emotional choreography** — characters cycling through emotions in predictable sequences (shock → denial → anger → acceptance) without the specific messiness of real emotional processing.

**Placeholder prose** — competent but generic sentences that could appear in any story. If a sentence could be moved to a different scene without anyone noticing, it's not doing enough work.

**Metaphor clusters** — the same family of metaphors appearing repeatedly. Weight/burden metaphors, light/dark metaphors, water/drowning metaphors. One or two is style; five in a chapter is a tic.

**Summary endings** — scenes that end with a paragraph summarizing the emotional significance of what just happened. "In that moment, she realized..." or "He knew then that nothing would ever be the same." Let the scene's events speak for themselves.

**Emotional inflation** — every moment treated as profound. A conversation about dinner plans carries the same emotional weight as learning about a betrayal. Not everything is significant. Understating small moments makes the big ones hit harder.

## Documented AI Failure Modes to Hunt For

Three failure modes documented in empirical research that should be explicit hunt targets, not just implicit concerns:

**Syntactic templating.** Are sentences falling into repeated structures even when the content changes? Does the prose have a rhythmic sameness that holds across paragraphs — same clause order, same modifier placement, same sentence length distribution? Shaib et al. (2024, EMNLP, https://aclanthology.org/2024.emnlp-main.368/) document that LLM sentence structures are copied from pretraining and not overwritten by alignment. Flag rhythmic sameness as a specific finding, not a side note under the Rhythm section. Note which structural pattern is repeating.

**Stock physical tells.** Is the writer reaching for clenched fists, shaky breaths, averted eyes, tightening jaws, quickening pulses, or other rubber-stamp body signifiers? These are what show-don't-tell produces when applied mechanically — the writer avoids labeling the emotion directly but substitutes a generic somatic signal that any character in any story could have. Flag every instance. The fix is not a different body part but a character-specific behavior that reveals how this particular person processes this particular feeling.

**Attractor-state fluency.** Does the prose feel "smoothed" rather than "written"? Is every passage competent in the same way — the same measured control regardless of whether the scene is mundane or devastating? Are emotional peaks getting the same tonal treatment as transitional moments? "Creativity Has Left the Chat" (2024, https://arxiv.org/abs/2406.05587) documents that alignment training creates attractor states in token distribution — not just word-level repetition but tonal and stylistic homogenization. Flag this as a holistic finding when the prose reads well but doesn't feel lived-in or variable.

These failure modes are empirically documented, not folklore. Treat any clear instance as a high-priority finding.
