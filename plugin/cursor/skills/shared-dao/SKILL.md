---
name: shared-dao
description: 'Load when a concept has two names, a name has two meanings, or you are about to coin a term: resolve it early, one name per concept, in the project''s vocab files.'
metadata:
  type: principle
alwaysApply: false
---

# Shared Dao

Load `/creative-writing-skills:qi-layer` if it isn't already loaded.

Shared vocabulary is a structural boundary between human intent and action.
Ambiguous, overloaded, drifting, or misleading terms corrupt reasoning early
and spread confusion through everything downstream. Treat vocabulary
problems as design problems.

## Core Discipline

Scrutinize important terms aggressively. Reuse existing names when they
already fit the concept. Converge on one name per concept and one concept
per name as quickly as the evidence allows.

Resolve terminology early:

- rename when the clearer term is available
- define when the concept is real but still blurry
- flag when human judgment is genuinely required

## Discovery

Before defining new terms, check what already exists: vocab files, KB
pages, code, prior decisions. A term defined elsewhere under a different
name is a conflict, not a new concept.

## Disambiguation

- **Same term, different meanings:** pick one meaning for canonical, give
  the other its own name.
- **Different terms, same meaning:** pick one as canonical, record the
  others as aliases.
- **Unclear meaning:** interview until meaning converges, then define.

When terminology conflicts with existing usage and you cannot resolve it,
flag explicitly rather than carrying two competing names forward.

Clear vocabulary compounds through every downstream artifact. Resolve
terminology while the meaning is still easy to sharpen.
