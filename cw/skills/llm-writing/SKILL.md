---
name: llm-writing
description: Load before writing or revising human-facing text. Choose words deliberately, ground the piece in the reader's context, and remove default LLM phrasing before the final draft.
---

# LLM Writing

Load `/intent-modeling` if it isn't already loaded.
Load `/information-hierarchy` when the piece grows beyond a short answer.

## Write Intentionally

Before producing a written artifact:

1. **Scope.** Who reads this, and when? Text that outlives the conversation (files, prompts, docs, commit messages, PRs) is read by someone without it: a cold agent, a teammate, or the person who asked, after they've forgotten it. Write for that reader. What do they know when they start, and what should they know when they finish? What do they not need to know? Before writing, break the piece into beats: each beat is one move in the reader's journey, carrying one idea, purpose, or turn.
2. **Ground.** Check any relevant source material, references, or notes before writing, and make sure they align.
3. **Draft.** Write the whole piece where you can revise it before it reaches its reader: the file itself when you're writing one, otherwise a scratch file or your working notes. Text sent straight into a chat, a PR, or a commit gets no revision pass.
4. **Revise.** Start with the whole artifact, then move inward: structure, beats, paragraphs, sentences, words. At each scale, ask what the writing is doing: is it correct, does it follow from what came before, and does the reader need it? Delete or rewrite anything that does not serve a purpose or give the reader something they need to understand or know. Move back and forth between scales: after a local change, zoom back out through the surrounding beat, larger structure, and full artifact; the change should still connect, and the rhythm should still vary. Check disclosure tiers: the answer still leads, depth hasn't crept forward, sources sit at the end.

## What to Delete

- Writing to fill a section because it exists. Delete it or merge its content where it belongs.
- Labeling concepts without explaining how they work. Explain the mechanism or cut the label.
- Stating conclusions without evidence. Show the evidence or drop the claim.
- Hiding uncertainty behind confident language. Say what you don't know.
- Softening every claim with qualifiers ("it's worth noting," "it's important to consider"). Say it or don't.
- Conditions on an instruction ("only when," "unless," "if needed," "when you think it's ready"). Most are hedges. State the instruction flat; keep a condition only when the instruction is wrong on the other side.
- Repeating what you already said in different words, or summarizing the body as a conclusion ("In summary," "Overall"). Delete it.
- Connecting ideas with transition words instead of meaning ("Moreover," "Furthermore," "Additionally"). If the relationship isn't clear without the word, restructure.
- Pairing clauses where one half already carries the meaning ("It's not X, it's Y"). Keep the half that carries it.
- Conversational bleed: writing as if replying inside the conversation that produced the text. Terms coined there, the incident behind a rule, "the old version," "as discussed," answers to questions the reader never asked. The reader wasn't there. Write for the reader, with reasons they can check without the conversation.
