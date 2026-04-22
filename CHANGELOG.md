# Changelog

## [Unreleased]

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
