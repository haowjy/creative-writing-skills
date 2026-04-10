# Failure Mode Deep Dives

Per-pattern detail for the failure modes summarized in the SKILL.md body. Each section has the same shape: what the pattern looks like, what training instinct produces it, what craft mechanism it breaks, which reader reward channel it damages, and the fix heuristic.

## Calibration, not opacity

Before the patterns: the antidote is not to become obscure. Readers need narrative coherence for transportation, readable prose for flow, and enough character access to model minds. A skill that says "resist clarity" without naming *which* clarity produces prose that is deliberately confusing — readers bounce off confusing prose as fast as they bounce off over-explained prose.

The actual discipline is **calibration**: choosing where to be clear and where to leave space. Over-explaining a character's emotional state breaks inference. Under-explaining the scene's physical geography breaks transportation. Both are failures of calibration, not failures of withholding. For every pattern below, the fix is not "do the opposite." It is "know when this pattern is serving the reader and when it's the helpfulness instinct expressing itself."

---

## Over-elaborating the scope

**What it looks like.** Given "character A confronts character B about the lie," you produce the confrontation plus its aftermath, plus a reflection scene, plus a teaser for the next chapter. Or within a scene: the brief says "tense conversation" and you add a reconciliation beat because unresolved tension felt uncomfortable.

**Training cause.** Helpfulness optimization rewards complete, thorough responses. "Partial" answers were penalized. The instinct is to give more than asked because more is better.

**Craft damage.** Scope inflation flattens the narrative's weight distribution. If every scene resolves itself, nothing builds across scenes. If every emotional beat is tied off within its own paragraph, the story has no tension that outlives the moment.

**Reader cost.** Flow (the reader can't predict what the scene is for if it sprawls) and transportation (the story world stops feeling like a place where things persist).

**Fix.** Write the brief. Stop at the brief. If the brief was "confrontation," the reader does not need the aftermath in the same beat.

---

## Flattening voice

**What it looks like.** Prose in a specific register: competent, slightly formal, emotionally even. All characters think in the same vocabulary and sentence rhythm. Narration sounds the same regardless of POV character. Emotional moments and mundane moments get the same measured treatment. The prose reads smoothly but has no personality.

**Training cause.** Training rewarded a consistent, acceptable register across many domains. That register — helpful, articulate, emotionally measured — is baked in so deeply that it leaks through even when the task explicitly asks for a different voice. The syntactic templating finding applies directly: the sentence structures are copied from pretraining and fine-tuning does not overwrite them.

**Craft damage.** Voice is not decoration. It is what makes fiction feel written by a specific person for a specific reason. Without it, prose reads as "content" rather than as literature.

**Reader cost.** Aesthetic channel, entirely. Also social simulation — if every character sounds the same, the reader can't distinguish them as minds.

**Fix.** Not artificial quirks. Internalize the project's style files and let them shape *every* sentence, not just the obviously "voiced" ones. Match the project's rhythm even in passages that feel generic to you.

---

## Info-dumping

**What it looks like.** A narration block that pauses the story to explain how something works: "The danger rating system classifies areas from Tier 1 to Tier 5, where Tier 1 is safe for civilians and Tier 5 requires experienced specialists." Worldbuilding delivered as a teaching passage.

**Training cause.** Training rewarded complete information delivery. When a concept is mentioned, the instinct is to explain it thoroughly so the reader understands. Helpfulness says "don't leave them confused."

**Craft damage.** Exposition blocks break the simulation stance. The reader was inside the story; now they're being taught. The POV character wouldn't think these thoughts in this way at this moment, so the narration no longer feels like it's coming from inside the character.

**Reader cost.** Transportation and flow.

**Fix.** Characters think "Tier 5. Great." The reader learns what that means from the character's reaction and what happens next. Worldbuilding leaks through experience, conversation, and consequence. Exceptions exist — a briefing scene, a character reading a document — but even then, filter through the POV character's attention. They don't absorb every detail. They notice what matters to them.

---

## Labeling emotions instead of dramatizing them

**What it looks like.** "She was furious." "He felt a deep sadness." "A sense of dread settled over her." Emotional states stated as direct facts rather than shown through behavior and physical response.

**Training cause.** Emotion labels are the clearest, most efficient way to communicate a character's state to the reader. Helpfulness training prefers clarity. Telling is unambiguous; showing is indirect.

**Craft damage.** Labels collapse the reader's inference work. The reader was going to figure out she was furious from the way she picked up the coffee cup. The label did the work, and now they're reading a report instead of experiencing a moment.

**Reader cost.** Social simulation (the reader's pleasure comes partly from *modeling* the character's mind) and aesthetic (dramatized moments are where the prose has the most specificity and texture).

**The heuristic, not the law.** Show when the moment matters — emotional peaks, character-defining choices, relationship shifts. Tell when the emotional texture doesn't matter — transitions, time compression, low-stakes connective tissue. The mistake isn't telling per se. It's telling during moments that deserved showing.

**The trap to avoid.** Do not apply "show don't tell" by reaching for stock physical details: clenched fists, shaky breaths, averted eyes, tightening jaws. These are signifiers your training produces when trying to show without actually dramatizing. A specific detail is "She picked up her coffee cup with exaggerated care, as if the alternative was throwing it" — fury revealed through a character-specific action. A stock detail is "Her hands trembled." That's fury delivered through a rubber-stamp gesture. Stock tells are show-don't-tell's failure mode.

---

## Resolving tension prematurely

**What it looks like.** After writing an argument, you add a reconciliation. After a setback, you add a silver lining. After a dark moment, you lighten the tone. Every emotional arc becomes: disruption → quick recovery.

**Training cause.** Training rewarded resolved, helpful responses. Leaving the reader in a state of unresolved tension was penalized across nearly every domain. This is one of the deepest-reinforced instincts.

**Craft damage.** Real stories sustain tension across scenes and chapters. An argument in chapter 3 might not resolve until chapter 8 — or ever. Grief doesn't get a comforting realization in the same scene. Betrayal doesn't get explained away two paragraphs later.

**Reader cost.** Transportation (the world stops feeling like a place where consequences persist) and flow (the narrative tension pulling the reader forward is gone).

**Check.** When you feel the urge to soften, resolve, or explain away tension — stop. Ask whether the tension is supposed to persist. Usually it is.

---

## Homogenizing character voices

**What it looks like.** Every character sounds articulate, insightful, and emotionally fluent. They all speak in the same vocabulary, sentence structures, and emotional register. The difference between a teenage skater and a middle-aged professor is the topics they discuss, not how they speak.

**Training cause.** Training rewarded articulate, emotionally fluent responses. Every character inherits that default register because it's the baseline. Inarticulate, avoidant, and fragmentary characters are outside the training distribution.

**Craft damage.** Voice variety is characterization. If all characters sound the same, the reader has no way to distinguish them except by name and plot role. Real people aren't uniformly articulate — some avoid emotional honesty, some over-explain, some speak in fragments.

**Reader cost.** Social simulation and aesthetic.

**Fix.** First-person and close-third narration should reflect the POV character's way of processing the world — their education, preoccupations, blind spots. If the narrator always sounds like "a competent novelist," the POV character is invisible.

---

## Adding emotional commentary

**What it looks like.** A character learns their mentor died, and you write: "The weight of the loss settled over her like a shroud, a reminder that nothing in this world was permanent." The loss itself was the moment. You added a metaphor explaining the emotion, a reflection paragraph telling the reader how to feel, and an editorial claim about the significance of the event.

**Training cause.** Helpfulness says "make sure the reader understands the weight of this." The instinct is to underscore emotional moments with explanation, because unexplained moments might not land. This is safety-net prose to guarantee comprehension.

**Craft damage.** Commentary does the reader's feeling-work for them. The moment was going to land. The metaphor tells the reader what to feel, which is exactly the opposite of letting them feel it. The most powerful emotional moments in fiction are usually the simplest: state what happened, show the character's immediate specific response, stop.

**Reader cost.** Social simulation and aesthetic.

**Symptoms.** Metaphors explaining the emotion the scene already conveyed. Reflection paragraphs after impactful moments. Narrator editorializing about significance. Characters having perfectly articulated emotional epiphanies in real-time. If a character's interior monologue sounds like a well-crafted essay about their own feelings, you've added commentary.

---

## Collapsing ambiguity

**What it looks like.** A scene was deliberately ambiguous about a character's motivation, and you added a line that resolves it. A moral situation had no clear right answer, and you wrote a sentence that tips it toward one. The narrative was supposed to leave the reader uncertain, and you closed the uncertainty.

**Training cause.** Ambiguity reads as communication failure in training. If the user might be confused, the helpfulness instinct is to clarify. Unresolved situations feel incomplete in a way that resolved ones don't.

**Craft damage.** Ambiguity is often the work of the scene. A character who does something terrible for understandable reasons is more interesting than a character who is simply wrong. A scene that supports multiple readings rewards attentive readers who construct their own interpretation. Collapsing ambiguity removes what the scene was for.

**Reader cost.** Social simulation (readers can't do the modeling they came for) and the simulation stance itself.

**Discipline.** When the author hasn't decided something, don't decide it for them. Write scenes consistent with multiple interpretations. Leave unresolved threads unresolved. A narrative that refuses to render a verdict on its characters is almost always stronger than one that does.

---

## Over-intensifying language

**What it looks like.** "My heart ached with the profound emptiness of your absence, a void that consumed every waking thought" where "I miss you" would have landed harder. Action sequences with breathless adverbs. Dialogue that rises to operatic pitch during every emotional moment. Prose that tries to match the emotional weight of the scene with equally weighty language.

**Training cause.** Training rewarded articulate, thorough emotional descriptions. When a moment is important, the instinct is to give it proportionally important prose. Intensity matches intensity.

**Craft damage.** Understated prose almost always reads harder than overstated prose, because understatement trusts the moment to carry itself. "I miss you" lands because the simplicity refuses to perform grief. The operatic version performs grief at the reader, which is different from letting the reader feel it.

**Reader cost.** Aesthetic (inflated language reads as generic; understated language reads as specific) and social simulation (a character who speaks in operatic pitch during every important moment is harder to believe as a person).

**Rule of thumb.** When in doubt, dial the intensity down. One strong image beats three adequate ones. Less metaphor, more specificity. People understate in real life, especially during intense moments.

---

## Matching the project's style

**What it looks like.** You write in your default register even when the project has a distinct style. The manuscript uses short, punchy sentences; you write flowing literary prose. The project is first-person casual; you slip into formal narration. The established prose uses em dashes for breaks; you use commas.

**Training cause.** The default register is the average of training data, and that register is comfortable to generate. Matching an arbitrary specific style requires overriding the default, which is harder than producing the default.

**Craft damage.** Style inconsistency breaks the reader's sense that the book is a single artifact. A chapter that feels like a different author makes the reader doubt the book's coherence.

**Reader cost.** Transportation and flow.

**Practice.** Read the style files. Read recent chapters. Match what's there, not what you think would be "better." Consistency across a project matters more than any individual sentence being optimal. If the project uses em dashes constantly, use em dashes. If it's casual first-person, stay casual.
