---
name: story-memory
type: mode-shift
description: >
  Information-first writing for story knowledge: wiki pages, vocab, decisions, canon summaries, and issue logs.
model-invocable: true
---

# Story Reference Writing

Load `/llm-writing` if it is not already loaded. This skill is for writing story
support material, not narrative prose. The goal is durable, source-aware,
information-first writing that future humans and agents can use.

Pick the mode that matches the artifact:

- **Fact extraction** — turn pages or sessions into durable story facts.
- **Wiki / reference writing** — explain a story concept clearly.
- **Vocabulary writing** — define canonical terms, aliases, and boundaries.
- **Decision capture** — record a settled creative choice and why it matters.
- **Issue logging** — preserve unresolved writing problems for future passes.

Use `/story-memory` for where files live, `/story-memory` for extracting
facts from manuscript pages, and `/shared-dao` for vocabulary discipline.
