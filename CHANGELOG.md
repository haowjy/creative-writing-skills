# Changelog

## [Unreleased]

## [0.0.15] - 2026-05-01

### Changed
- 3 orchestrators (`story-orchestrator`, `draft-orchestrator`, `knowledge-orchestrator`): scoped Bash tool allowlists to `meridian spawn/work/context/session` + read commands. Unrestricted `Bash` on coordinator-altitude agents created escape hatches that undermined the delegation model.
- `explorer`, `continuity-checker`: added `Bash(meridian kg *)` to tool allowlists — bodies referenced `meridian kg graph` but scoped tools didn't permit it.
- `draft-orchestrator`: added explicit `reader-sim` dispatch (post-convergence experiential pass) and `continuity-checker` dispatch (deep cross-project checks). Previously only documented in README/architecture but not operationalized in the orchestrator prompt.
- `draft-orchestrator`: now promotes recurring critic findings to `kb/issues/` — critics are read-only and report as spawn output.
- `reader-sim`: removed file-writing instructions (agent is read-only, reports as spawn output). Trimmed four-channel restatement to reference loaded `writing-principles` skill.
- `writing-artifacts`: fixed ownership table — critics report findings as spawn output, `draft-orchestrator` promotes to `kb/issues/`. `work/critique-reports/` written by draft-orchestrator synthesis, not critics directly.
- `docs/architecture.md`: replaced stale `knowledge-graph`/`mermaid` with `md-validation` in skill dependency diagram. Fixed `character-sim` model (sonnet, not unset). Updated artifact flow for read-only critics. Updated skill reuse summary.
- `README.md`: fixed skill count (12, not 13), updated skill table (removed deleted `prose-analysis`/`knowledge-graph`/`python-tool-runner`, added `writing-issues`/`orchestrate`), fixed project layout to match `writing-artifacts` conventions, updated draft loop diagram for reader-sim as post-convergence pass.

## [0.0.14] - 2026-05-01

### Changed
- 7 agents (`graph-maintainer`, `chronicler`, `wiki-editor`, `explorer`, `outliner`, `continuity-checker`, `knowledge-orchestrator`): replaced `knowledge-graph` and `mermaid` skills with `md-validation` from meridian-base. Agent bodies now reference `meridian kg graph`, `meridian kg check`, `meridian mermaid check` instead of bundled scripts.

### Removed
- `knowledge-graph` skill — superseded by `meridian kg` (link topology tree, broken link checks). The bundled `graph.py` script is no longer needed.
- `mermaid` skill — superseded by `meridian mermaid check` + `md-validation` skill from meridian-base. The bundled `check_mermaid.py` script is no longer needed.
- `meridian-cli` from all agent skill lists (skill deleted from meridian-base). Body references in `explorer` and `session-miner` updated to use `meridian session` CLI commands directly.

## [0.0.9] - 2026-04-22

### Added
- `orchestrate` skill — shared coordination model for orchestrators (delegation discipline, convergence loops, critique synthesis with reader reward channels, artifact persistence)
- `mermaid` skill — diagram syntax reference for structure-producing agents
- `docs/architecture.md` — mermaid diagrams for spawn hierarchy, skill dependencies, model routing, and artifact flow
- `AGENTS.md` — agent guidance for working with this repository
- Model aliases in `mars.toml` — opus, sonnet, haiku, mini, codex, gpt with provider/harness routing
- Mechanical prose analysis bundled into `prose-critique` as optional tooling (analyze.py, antipatterns.md, baseline.md)

### Changed
- All 17 agents: tightened `tools:` and `disallowed-tools:` to match dev-workflow discipline — orchestrators get `Bash(meridian spawn *)`, workers get scoped tools, read-only agents get specific allowlists, destructive git ops blocked everywhere
- All 3 orchestrators now load `orchestrate` skill; removed duplicated delegation boilerplate and critic synthesis methodology from agent bodies
- Story-orchestrator: trimmed skills list from 10 to 8, removed inline reader reward channel triage (now in orchestrate skill)
- Shell scripts (graph.sh, analyze.sh) replaced with Python equivalents (graph.py, analyze.py)
- `story-context` updated to use `meridian context kb` / `meridian context work` path resolution
- `writing-artifacts` layout and promotion rules refined
- Various skill content improvements across brainstorming, knowledge-graph, story-decisions, wiki-docs, writing-issues, writing-staffing resources

### Removed
- `prose-analysis` skill — resources moved to `prose-critique` as optional mechanical analysis
- Shell scripts: `graph.sh`, `analyze.sh` — replaced by Python versions
