---
name: llm-writing
description: 'Load before you write a report to the user, doc, prompt, README, KB page, AGENTS.md or .context/ page, changelog entry, issue, commit message or PR body: name the reader and what they know, write to them in plain words, and strip default LLM phrasing.'
metadata:
  type: guardrail
---

# LLM Writing

Load `/creative-writing-skills:intent-modeling` if it isn't already loaded.

## Write for the Reader

Before you draft, state who the reader is and what they know when they start: what they already have (the project, its terms, the pages they've read) and what they lack (the files you read and the commands you ran, the names you coined while working, the reasons behind choices made here). Add what they came for.

Every reader lacks something you have. The person who asked was in the conversation but didn't see your work, so a reply in chat needs this as much as a file does. Text that outlives the conversation (files, prompts, docs, commit messages, PRs) is read by someone without the conversation too: a cold agent, a teammate, or the person who asked, after they've forgotten it. Skip this step and you write for yourself, and it reads fine to you.

Then write to that reader: lead with what they came for, give them what they lack, skip what they already have, and cut what only serves you. Break the piece into beats, each one move in the reader's journey. Check the source material it rests on.

Draft the whole piece where you can revise it before it reaches its reader: the file itself, or a scratch file. Text sent straight into a chat, a PR or a commit gets no revision. Revise from the whole piece down to the words, as the reader you named: is each part correct, does it follow from what came before, can they follow it with what they know, and do they need it? After a local change, reread the beat around it.

## Choose Words

- Use the short, everyday word: "use", not "utilize"; "help", not "facilitate". A long word has to buy its length with precision.
- The project's own names are the word list. Write the real name as the project spells it, whether a symbol, a file, a flag, a character, or an invented term, not a synonym or a description of it, and call each thing by one name everywhere.
- Don't invent jargon. Use the words the reader would say out loud ("move", "delete", "a budget that only decreases"), not a coined metaphor ("evacuate", "ratchet"). A named pattern is fine when the text says what it means the first time.
- Be specific over sterile: not "schema changes can cause issues" but "a column rename fails the build".
- Vary the rhythm. Short sentences land a point; longer ones carry a fact with its condition or consequence. Split the sentence that carries two thoughts; keep the long one that carries one.
- Leave no sentence open to two readings: "only" and "not" next to the word they change, every "it" and "this" pointing at one noun, no noun strings. The cases and a before/after are in `resources/word-choice.md`.

## What to Delete

- Writing to fill a section because it exists. Delete it or merge its content where it belongs.
- Labeling concepts without explaining how they work. Explain the mechanism or cut the label.
- Stating conclusions without evidence. Show the evidence or drop the claim.
- Hiding uncertainty behind confident language. Say what you don't know.
- Softening every claim with qualifiers ("it's worth noting," "it's important to consider"). Say it or don't.
- Repeating what you already said in different words, or summarizing the body as a conclusion ("In summary," "Overall").
- Connecting ideas with transition words instead of meaning ("Moreover," "Furthermore," "Additionally"). If the relationship isn't clear without the word, restructure.
- Pairing clauses where one half already carries the meaning ("It's not X, it's Y"). Keep the half that carries it.
- Conversational bleed: writing as if replying inside the conversation that produced the text. Terms coined there, labels and IDs minted during the work (a ruling number, a finding ID, a lane name), the incident behind a rule, links into a work directory or anything else that won't last, "the old version," "as discussed," answers to questions the reader never asked. The reader wasn't there. Write for the reader, with reasons they can check without the conversation.

To commission a cold read of durable pages, and act on its findings, open `resources/cold-read.md`.
