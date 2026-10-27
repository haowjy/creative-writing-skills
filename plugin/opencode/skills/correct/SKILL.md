---
name: correct
description: 'Use when the human wants the mistakes agents keep repeating fixed for good. Works the KB corrections register: fixes each recurring class at the strongest level that holds (remove the wrong way, an automated check, a tool permission, a written rule last), proves each fix on a real past mistake, and updates the register.'
metadata:
  type: mode-shift
---

# Correct

The human keeps correcting agents for the same mistakes. Change the project
or the prompts so the next agent can't make them.

Assume every contributor is an agent that sees only the files it opened,
copies the nearest example, and takes the shortest path that works. Design so
a change that looks right from one file is right for the whole project.

In a code project, load `resources/code.md`: it adds architecture, types, and
tests to the levels below.

## Find the Classes

Start from the KB corrections register (`/creative-writing-skills:knowledge-layers`
`resources/corrections/`) and any correction the human just gave. Add what the
register missed: mine recent sessions with `@session-miner`, and read work the
human undid or redirected and recent review findings. A class counts once it
has happened twice or the human names it; record other single occurrences as
candidates.

## Fix Each Class at the Strongest Level That Holds

1. **Remove the wrong way.** Give each piece of state one owner and each task
   one supported way. Replace hand-synced copies with one source of truth.
   Delete the old way and the examples an agent would copy.
2. **An automated check** that fails and names what to do instead: a
   validator, a schema, a check script. Where the pattern is already
   common, fail only on additions.
3. **A tool permission** in the agent profile, for agent behavior a tool rule
   can block: a denied command, a read-only tool set.
4. **A written rule, last**, for judgment calls nothing can check. Put it
   where the agent reads it at the moment of choice: the nearest `AGENTS.md`,
   or the skill or agent prompt that governs that step, edited in its source
   package.

## Fix and Prove

Fix the most frequent classes first, one change each. Prove each new check
fails on a real past mistake: replay the change that made it and show the
failure. An exception goes where the check fires, with a reason and the
human's approval.

## Update the Register

Set each class's **Enforced by** to what now catches it. Delete a row once
its mistake can no longer happen. When a class recurs under a written rule, look again for a stronger level. If
none holds, sharpen the rule, move it closer to the moment of choice, and
report the class as a judgment risk that remains.

## Report

Each class with its evidence, the level you picked, and why a stronger level
didn't work.
