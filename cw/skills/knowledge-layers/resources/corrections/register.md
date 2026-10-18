# Corrections Register

The register records each time the human corrects an agent, grouped by the
mistake behind it, so a mistake that recurs gets fixed where the next agent
can't repeat it. It lives at the KB root as `corrections.md`; create it on
first use. The local KB guide wins on format.

## What Counts

A correction is the human saying an agent's work or behavior was wrong:
pushing back, repeating an instruction the agent ignored, undoing or
redirecting its work, or stating a rule because an agent broke it. The human
choosing between sound options is a decision, and goes in the decision index.

## Classes

Group by the underlying mistake, not the wording. "Answered from memory
instead of reading the source" and "quoted a figure without checking it" are
one class: claiming without checking. Write the correct behavior with the
calibration the human gave it: "lean toward X" stays a lean, not a ban on
everything else.

## Format

One table, then a candidates list:

| Class | Correct behavior | Enforced by | Occurrences |
|---|---|---|---|
| What the agent did, one line | What the human wanted, one line | What prevents or catches the mistake, by kind and location: a structural change, an automated check, a tool permission, a written rule (name the file), or `none` | `chat:c123` or `spawn:p123`, date, a short quote; one per line |

A class seen once goes under **Candidates** with its occurrence and moves into
the table on its second. Delete a row once its mistake can no longer happen;
git history keeps it.

In a code project, record **Enforced by** with the kinds in `code.md`.

## Recording

When you mine a conversation, record each correction in it: a new occurrence
on its class, or a new candidate. Identify an occurrence by its session and
message; a correction already recorded is not a new one.

A correction that gives a class its second occurrence, or any later one, is a
repeat. Report repeats
to the caller for `/correct`, and flag any that recurred despite a check or
permission: that enforcement failed.
