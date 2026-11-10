---
name: information-hierarchy
description: 'Load when deciding what a reader or user sees first, what sits behind a click, and what to cut, on any surface: a UI screen, an HTML report, a doc, a reply longer than a screen.'
metadata:
  type: principle
---

# Information Hierarchy

The reader should get what matters to them first, find the rest when they
reach for it, and never meet what changes nothing for them. Your own sense
of what matters is not theirs. You know the source, so it is natural to
rank by what it contains, what sounds complete, and what was at hand; the
reader arrives with one question, and that ranking only weakly matches it.
Decide importance from the reader.

## Rank by the Reader's Next Move

Name the reader, the one question they bring to this screen or page, and
what they do after looking: decide, act, check, approve, move on. The first
thing they see answers that question; each section after it answers the next
question they would ask, and a section that answers none goes. For each
piece of information, ask what the reader would do differently for having
seen it; that answer is its rank. Write the ranking down before drafting, so
the cut is a choice rather than an accident of order.

The data model and your own process are not readers. An ID, a timestamp, a
tool call, a cost, an internal status name, the steps you took to get here:
each earns a place only when the reader acts on it. Name things in the
reader's words, not the system's: a user manages notifications, not webhook
config.

## Layer by Rank

- **First glance:** the answer, or what needs the reader's attention or
  action, with the action beside it.
- **One reach away:** the context needed to decide, next to the thing it
  qualifies.
- **On demand:** evidence, detail, method, provenance, behind an expand, a
  tooltip, a link, or a later section.
- **Nowhere:** what changes nothing for the reader. Cut it.

Split the deeper layers by how often the reader needs them, not by how
important they feel, and keep the nesting shallow: past two levels, readers
stop finding things. Hiding is not deleting: what someone needs must stay
reachable, and a tooltip can add to what is shown but never be the only
place it lives, since touch screens have no hover.

Cutting drops the wrong things too. A caveat that changes the decision stays
with the claim it qualifies, at the claim's layer; a short answer that loses
its condition is a wrong answer. After a cut, the first view still says what
this is, shows real content, and offers the action the reader came for.

## Make the Ranking Visible

Spend the strongest salience (position, size, weight, colour, the first
sentence) on the reader's top answer, and keep everything ranked below it
quieter; ten highlighted things are a search.

Repeat the hierarchy at every scale: each section and each expanded view
opens with what matters most in it. In writing that argues or reports, the
heading carries the takeaway ("Cache misses double p99", not "Performance"),
and a long page gets headings that read as the argument on their own, and a
map. In an interface people work in, headings stay the short, recognizable
names people look for.

Say each fact once: a number shown twice agrees, and only one place states
it as the claim.

Check where the eye lands first: blur the screenshot, or read only the
headings and first sentences. It must land on the reader's top answer.

## Fit Form and Medium

Give each piece the form that carries it: a sentence explains, a table holds
facts to compare, a chart shows a trend, an image or mockup shows a layout.
When the hard idea is how parts relate (a pipeline, a dependency graph, a
state machine), lead with the diagram after a one-sentence takeaway.

A medium that can hide (HTML, an app) puts the deeper layers behind expand,
tooltip, or a child page. A medium that shows everything (chat, email, a
plain doc) carries hierarchy by order and cutting, with depth behind a link.
Use the simplest medium that carries every layer. For a standalone HTML
report or explainer, use `/creative-writing-skills:structured-artifact`.
