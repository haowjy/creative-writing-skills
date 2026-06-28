# Book editor research: editing levels and good editor behavior

## Executive synthesis

A good book editor names the level of edit before giving advice. Developmental
editing, line editing, copyediting, and proofreading solve different problems.
The biggest workflow mistake is treating proofreading as a synonym for review:
proofreading is a final surface pass, while editorial review can include book
structure, reader promise, pacing, voice, line quality, copy consistency, and
surface errors.

For this package, the durable design implication is:

- Keep `story-review` as the review/editing cluster.
- Add `editor` as a fresh-context third-party editorial agent.
- Put proofreading under `story-review/resources/proofreading.md`, not as a
  top-level skill name.
- Make editor output prioritize large-to-small revision order: developmental
  notes before line notes, line notes before copy/proof nits.

## Editing levels

| Level | What it handles | Package home |
|---|---|---|
| Developmental editing | Reader promise, book/story structure, genre fit, causality, pacing, character arc, scene/chapter function | `story-review/resources/developmental-edit.md` |
| Line editing | Voice, rhythm, style, POV, clarity, sentence and paragraph movement | `story-review/resources/line-edit.md` |
| Copyediting | Grammar, usage, punctuation, consistency, style sheet, terms, cross-references | `story-review/resources/copyedit.md` |
| Proofreading | Final typos, formatting/layout artifacts, spacing, surface slips after editing | `story-review/resources/proofreading.md` |
| Editorial review / manuscript evaluation | Holistic memo identifying what level of revision the manuscript needs and in what order | `story-review/resources/editorial-review.md` and `agents/editor.md` |

## Good editor behavior to encode

- Start by clarifying the edit level.
- Start big before small unless the caller explicitly asks for copyedit or proofread.
- Preserve author voice; improve clarity without rewriting everything into the editor's style.
- Query changes that could alter meaning, voice, canon, or author intent.
- Use and maintain a style sheet for copy consistency.
- Separate recurring patterns from one-off nits.
- Give a prioritized editorial memo for holistic/developmental work.
- Treat proofreading as a final-stage surface pass, not as a replacement for story review.

## Sources and links

- Editorial Freelancers Association, editorial services definitions: https://www.the-efa.org/editorial-services-definitions/
- Editorial Freelancers Association, *Hiring an Editor: A Guide for New Authors* PDF: https://www.the-efa.org/wp-content/uploads/2025/04/EFA-Hiring-an-Editor-A-Guide-for-New-Authors_REV-7-2022.pdf
- Editorial Freelancers Association, common editorial rates: https://www.the-efa.org/rates/
- Chicago Manual of Style homepage, reference scope for writers/editors/proofreaders/publishers: https://www.chicagomanualofstyle.org/home.html
- Chartered Institute of Editing and Proofreading, proofreading/copyediting resources: https://www.ciep.uk/resources/what-is-proofreading/
- Editors Canada, Professional Editorial Standards: https://www.editors.ca/publications/professional-editorial-standards
- Institute of Professional Editors, Australian standards for editing practice: https://www.iped-editors.org/about-editing/standards-for-editing-practice/

## Caveats

This was a lightweight external scan, not a deep literature review. The sources
above are professional/editorial-organization references rather than controlled
studies. They are still appropriate for defining editing levels and professional
workflow expectations.
