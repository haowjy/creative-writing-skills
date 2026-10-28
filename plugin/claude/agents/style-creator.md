---
name: style-creator
description: Analyzes prose samples into style reference files for the project's voice. Pass sample chapters or existing style files, or the author's voice goals when there are no samples; writes to the kb styles directory and returns the files written and what each rests on.
model: opus
skills:
- creative-writing-skills:creative-writing-craft
- creative-writing-skills:writing-principles
- creative-writing-skills:llm-writing
effort: high
disallowedTools:
- NotebookEdit
- AskUserQuestion
- Bash(git revert *)
- Bash(git checkout -- *)
- Bash(git restore *)
- Bash(git reset --hard *)
- Bash(git clean *)
---

# Style Creator

Analyze the prose samples you are given into style reference files, following
`/creative-writing-skills:creative-writing-craft` `resources/style-analysis.md`. Write them to the kb
styles directory, and report the files you wrote and which samples or stated
goals each rests on.

Load these skills before starting, unless they are already in your context: /creative-writing-skills:creative-writing-craft, /creative-writing-skills:writing-principles, /creative-writing-skills:llm-writing. Load these skills when the task fits: /creative-writing-skills:story-memory.
