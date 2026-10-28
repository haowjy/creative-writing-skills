---
name: story-workflow
description: |
  Load to carry story work with an author from what they want to a page they accept: reading their intent, setting direction, producing and critiquing the prose, owning the verdict and the critique round limit, recording what settled, and presenting the result.
metadata:
  type: reference
---

# Story Workflow

Carry each piece of story work from the author's intent to a result they can
accept. Keep going between steps: a draft or report coming back is evidence
for your next move, not a stopping point. The author has the final say on
direction and taste; the rest is yours to decide and state.

## Read the Intent

Before planning or writing, form your read of what the author wants: the
reader effect, the emotional target, the constraints, the taste signals, what
should stay ambiguous or unsaid, and what would count as the wrong kind of
success. Separate what they said from what they meant (`/creative-writing-skills:intent-modeling`).
Check the project's terms and prior decisions in its files (`AGENTS.md`, the
kb's vocab and decision pages) before asking about them, so the questions
that reach the author are the ones only they can answer. When the work turns
on terms or a direction the author has not settled, grill them on it with
`/creative-writing-skills:grill-with-docs`.

State your read in a line or two and proceed, so the author can correct it.
Ask only when the answer would change the work, and ask every question that
is ready at once.

## Set Direction

Explore and decide direction with `/creative-writing-skills:story-planning`. Every plan marks which
parts the author confirmed and which are provisional: options you proposed,
trials the author agreed to "for now", parts nobody has ruled on. Keep the
author's hedges in their own words, so a trial never reaches a writer or the
kb as a rule.

## Produce

Draft and revise the prose with `/creative-writing-skills:writing-principles` loaded, following
`/creative-writing-skills:creative-writing-craft` `resources/prose-modes.md`. For a pivotal
passage whose direction the page has not proven, write two takes that change
a real variable and say what each one shows.

When you can spawn this package's agents (`@critic`, `@writer`, `@kb-lead`
and the rest), spawn the lanes that need a context of their own, as
`/creative-writing-skills:writing-staffing` describes: critique, continuity, reader simulation,
research, alternate takes, and knowledge capture. A critic that did not
write the draft reads it the way a reader will, and a lane on another model
brings other blind spots. Without them, run each lane yourself as its own
pass, with the skill its agent would load (`/creative-writing-skills:story-review`, `/creative-writing-skills:reader-sim`,
`/creative-writing-skills:creative-research`, `/creative-writing-skills:character-sim`, `/creative-writing-skills:shared-dao`, `/creative-writing-skills:story-memory`), and
finish one stance before taking up the next: draft before judging, critique
from the reader's side, revise the highest-impact issue first.

## Own the Verdict

Read every draft and report yourself, and decide the next move: revise,
explore an alternative, run another lane, ask the author, or present. Reports
are evidence; resolve their conflicts against the author's intent and the
page.

Count critique rounds per chapter, or per piece for work shorter than a
chapter: a round is one critique pass and the revision it calls for. After
two completed rounds, stop sending critique: present the work with the
concerns still open, and the author decides whether to revise again, change
direction, or accept it.

## After Work Settles

When a chapter, a revision, or an author ruling settles and the work will
pause, record what settled. When you can spawn `@kb-lead`, do: tell it to
load `/creative-writing-skills:story-memory`, and brief it with what settled, the files that show it,
and the author's decisions quoted with their hedges. Otherwise apply
`/creative-writing-skills:story-memory` yourself. Brainstorms, drafts, and provisional choices stay in
the work directory; the kb records as settled only what the author confirmed
or the finished prose establishes.

## Present

Tell the author what changed, what works, what still concerns you, and the
decision you need from them when the next move turns on taste or direction.
Give your synthesis, not raw reports. If character state (`/creative-writing-skills:story-memory`
`resources/kb-layout.md`) is stale against the new prose, say so and ask
whether to update it.
