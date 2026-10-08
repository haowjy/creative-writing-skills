#!/usr/bin/env python3
"""
Build and lint the `cw/` Claude/plugin distribution (skills + agents).

`cw/skills/` and `cw/agents/` each split into two kinds:

  GENERATED  Copied from a temporary Mars consumer project's `.claude/` output.
             Mars performs the harness lowering; this script only filters the
             components that belong in the cw distribution. Run with --apply to
             refresh them; check mode fails on drift.

  MANUAL     cw-only or cw-adapted components. Some are manual because their
             Mars output contains Meridian-specific vocabulary. The tool never
             overwrites these; it only lints them.

Usage:
  python scripts/sync_cw_skills.py            # full check: Mars build + drift + lint
  python scripts/sync_cw_skills.py --lint     # lint only (no Mars build); use in CI
  python scripts/sync_cw_skills.py --apply    # run Mars sync + refresh GENERATED components
  python scripts/sync_cw_skills.py --list     # print classification and exit
"""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
CW_SKILLS = REPO / "cw" / "skills"
CW_AGENTS = REPO / "cw" / "agents"

# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

# Skills shipped in the cw distribution from Mars-lowered `.claude/skills/`.
# Keep this filtered: dependency packages contain many operational skills that
# do not belong in a creative-writing plugin.
GENERATED_SKILLS = [
    # creative-writing-skills source skills
    "character-sim",
    "creative-research",
    "creative-writing-craft",
    "creative-writing-modes",
    "creative-writing-muse",
    "reader-sim",
    "story-memory",
    "story-planning",
    "story-review",
    "writing-principles",
    # dependency skills intentionally bundled into cw
    "information-hierarchy",
    "intent-modeling",
    "knowledge-layers",
    "llm-writing",
    "qi-layer",
    "reflect",
    "structured-artifact",
]

# Hand-maintained cw-only skills the tool lints but never overwrites.
MANUAL_SKILLS = [
    # local skills carrying cw-specific adaptations
    "writing-staffing",
    # dependency skills that need cw-specific de-Meridianization
    "grill-with-docs",
    "shared-dao",
    # base skills with Meridian CLI refs replaced
    "md-validation",
    "zoom-out",
    # cw-only, no upstream Mars source
    "kb-management",
    "project-setup",
]

# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

# Agents shipped from Mars-lowered `.claude/agents/`.
# Mars strips harness-specific frontmatter (tools, sandbox, subagents,
# model-policies, approval) and converts skills to Claude format.
GENERATED_AGENTS = [
    "brainstormer",
    "character-sim",
    "continuity-checker",
    "critic",
    "editor",
    "muse",
    "outliner",
    "reader-sim",
    "style-creator",
    "web-researcher",
    "writer",
]

# Hand-maintained cw-only agents the tool lints but never overwrites.
MANUAL_AGENTS: list[str] = []

# ---------------------------------------------------------------------------
# Lint patterns
# ---------------------------------------------------------------------------

# Vocabulary that should never leak into any cw file (command/env/infra refs).
CW_LEAKS = re.compile(
    r"\bmeridian spawn\b|\$?MERIDIAN_[A-Z_]+|--from\b|/meridian-spawn"
    r"|deny_headless"
    r"|@(?:bard|lore-keeper|explorer|kb-writer|kb-maintainer|session-\w+)",
)

# Mars-only frontmatter keys (cw must use Claude vocab: name + description).
MARS_FRONTMATTER = re.compile(r"^(type|model-invocable|effort|model-policies|sandbox):", re.M)

# Known non-agent @ references (CSS at-rules, library imports, etc.).
AT_ALLOWLIST = {
    "anthropic", "kb-lead",
    # CSS at-rules / library imports (not agent refs)
    "apply", "import", "layer", "media", "property", "supports",
    "tailwindcss", "theme", "xyflow",
}


def split_frontmatter(text: str):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[:1], lines[1:i], lines[i:]
    return None, None, text


def body_of(path: pathlib.Path) -> str:
    _, _, rest = split_frontmatter(path.read_text())
    return "".join(rest) if isinstance(rest, list) else rest


def _dir_differs(a: pathlib.Path, b: pathlib.Path) -> bool:
    af = {p.relative_to(a): p for p in a.rglob("*") if p.is_file()}
    bf = {p.relative_to(b): p for p in b.rglob("*") if p.is_file()}
    if set(af) != set(bf):
        return True
    return any(af[k].read_bytes() != bf[k].read_bytes() for k in af)


def copy_skill_dir(src_dir: pathlib.Path, dst_dir: pathlib.Path) -> bool:
    """Replace one generated cw skill with the full Mars-lowered skill dir."""
    if not (src_dir / "SKILL.md").is_file():
        raise FileNotFoundError(f"Missing {src_dir / 'SKILL.md'}")
    if dst_dir.is_dir() and not _dir_differs(src_dir, dst_dir):
        return False
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)
    return True


def _scrub_agent(text: str) -> str:
    """Post-process a Mars-lowered agent to remove residual harness vocabulary.

    Mars lowering doesn't fully strip all harness-specific frontmatter and tool
    permissions for Claude targets. This cleans up what it misses:
    - Tool lines referencing meridian commands
    - Mars-only frontmatter keys (effort, etc.) not caught by lowering
    """
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        # Drop tool permissions referencing meridian
        if re.match(r"^-\s+Bash\(meridian\b", line):
            continue
        # Drop Mars-only keys that survived lowering
        if re.match(r"^effort:", line):
            continue
        out.append(line)
    return "".join(out)


def copy_agent_file(src: pathlib.Path, dst: pathlib.Path) -> bool:
    """Replace one generated cw agent with the scrubbed Mars-lowered agent file."""
    if not src.is_file():
        raise FileNotFoundError(f"Missing {src}")
    scrubbed = _scrub_agent(src.read_text())
    if dst.is_file() and dst.read_text() == scrubbed:
        return False
    dst.write_text(scrubbed)
    return True


def build_claude_output() -> pathlib.Path:
    """Return a temp `.claude/` dir built from this package as a dependency."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="cw-mars-consumer-"))
    mars_toml = tmp / "mars.toml"
    repo_path = str(REPO).replace("\\", "/")
    mars_toml.write_text(
        f"""[dependencies.creative-writing-skills]\npath = \"{repo_path}\"\n\n[settings]\ntargets = [\".claude\"]\nagent_emission = \"always\"\nmodels_cache_ttl_hours = 24\n"""
    )
    env = os.environ.copy()
    env.pop("MERIDIAN_MANAGED", None)
    cmd = ["meridian", "-C", str(tmp), "mars", "sync", "--no-refresh-models"]
    result = subprocess.run(cmd, cwd=tmp, env=env, text=True, capture_output=True)
    if result.returncode != 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"Mars temp consumer sync failed: {' '.join(cmd)}")
    return tmp / ".claude"


def bundled_skill_names() -> set[str]:
    return {d.name for d in CW_SKILLS.iterdir() if d.is_dir()}


def bundled_agent_names() -> set[str]:
    return {p.stem for p in CW_AGENTS.glob("*.md")}


def agent_skill_refs(path: pathlib.Path) -> list[str]:
    """Parse the `skills:` block of an agent, ignoring prose like descriptions.

    Handles both Mars format (`creative-writing-skills:skill-name`) and
    Claude/lowered format (bare `skill-name`).
    """
    _, fm, _ = split_frontmatter(path.read_text())
    if fm is None:
        return []
    refs, in_block = [], False
    for line in fm:
        if re.match(r"^skills:", line):
            in_block = True
            continue
        if in_block:
            # Mars format: `- creative-writing-skills:skill-name`
            m = re.match(r"\s*-\s*creative-writing-skills:([a-z0-9-]+)", line)
            if m:
                refs.append(m.group(1))
                continue
            # Claude/lowered format: `- skill-name`
            m = re.match(r"\s*-\s*([a-z][a-z0-9-]+)\s*$", line)
            if m:
                refs.append(m.group(1))
                continue
            if line[:1] not in (" ", "\t", "\n", ""):
                break
    return refs


def run(apply: bool, lint_only: bool = False) -> int:
    problems: list[str] = []
    notes: list[str] = []

    # 1–2. Sync or drift-check GENERATED components (skipped in lint-only).
    # Drift checks rebuild from Mars and diff — useful locally to catch
    # forgotten --apply runs, but fragile in CI where the resolved
    # meridian-base version may differ from what was synced locally.
    if not lint_only:
        claude_root: pathlib.Path | None = None
        try:
            claude_root = build_claude_output()
        except Exception as exc:
            problems.append(str(exc))

        generated_skills_root = claude_root / "skills" if claude_root else None
        generated_agents_root = claude_root / "agents" if claude_root else None

        # 1. Sync or drift-check GENERATED skills.
        if generated_skills_root is not None:
            for name in GENERATED_SKILLS:
                src_dir = generated_skills_root / name
                cw_dir = CW_SKILLS / name
                if not src_dir.is_dir():
                    problems.append(f"GENERATED skill {name} missing from Mars .claude/skills output")
                    continue
                if apply:
                    if copy_skill_dir(src_dir, cw_dir):
                        notes.append(f"synced skill {name}")
                else:
                    if not cw_dir.is_dir():
                        problems.append(f"{name}: cw/skills/{name}/ missing (run --apply)")
                        continue
                    if _dir_differs(src_dir, cw_dir):
                        problems.append(f"{name}: cw skill dir drifted from Mars .claude output (run --apply)")

        # 2. Sync or drift-check GENERATED agents.
        if generated_agents_root is not None:
            for name in GENERATED_AGENTS:
                src = generated_agents_root / f"{name}.md"
                dst = CW_AGENTS / f"{name}.md"
                if not src.is_file():
                    problems.append(f"GENERATED agent {name} missing from Mars .claude/agents output")
                    continue
                if apply:
                    if copy_agent_file(src, dst):
                        notes.append(f"synced agent {name}")
                else:
                    if not dst.is_file():
                        problems.append(f"{name}: cw/agents/{name}.md missing (run --apply)")
                        continue
                    if _scrub_agent(src.read_text()) != dst.read_text():
                        problems.append(f"{name}: cw agent drifted from Mars .claude output (run --apply)")

    # 3. Classification completeness: every cw component must be classified.
    classified_skills = set(GENERATED_SKILLS) | set(MANUAL_SKILLS)
    bundled_skills = bundled_skill_names()
    for unknown in sorted(bundled_skills - classified_skills):
        problems.append(f"cw/skills/{unknown} is unclassified — add it to GENERATED_SKILLS or MANUAL_SKILLS")
    for missing in sorted(classified_skills - bundled_skills):
        problems.append(f"{missing} is classified but missing from cw/skills/")

    classified_agents = set(GENERATED_AGENTS) | set(MANUAL_AGENTS)
    bundled_agents = bundled_agent_names()
    for unknown in sorted(bundled_agents - classified_agents):
        problems.append(f"cw/agents/{unknown} is unclassified — add it to GENERATED_AGENTS or MANUAL_AGENTS")
    for missing in sorted(classified_agents - bundled_agents):
        problems.append(f"{missing} is classified but missing from cw/agents/")

    # 4. Lint all cw skills: Claude frontmatter, no leaks (SKILL.md + resources).
    for md in sorted(CW_SKILLS.glob("*/SKILL.md")):
        _, fm, _ = split_frontmatter(md.read_text())
        fm_text = "".join(fm or [])
        if MARS_FRONTMATTER.search(fm_text):
            problems.append(f"{md.relative_to(REPO)}: Mars-only frontmatter key")
        if "name:" not in fm_text:
            problems.append(f"{md.relative_to(REPO)}: missing `name`")
        m = CW_LEAKS.search(md.read_text())
        if m:
            problems.append(f"{md.relative_to(REPO)}: leaked Meridian vocab {m.group(0)!r}")
    # Also lint resource files for leaks.
    for md in sorted(CW_SKILLS.rglob("resources/*.md")):
        m = CW_LEAKS.search(md.read_text())
        if m:
            problems.append(f"{md.relative_to(REPO)}: leaked Meridian vocab {m.group(0)!r}")

    # 5. Lint cw agents: skills refs resolve, no leaks, Claude frontmatter.
    agent_names = bundled_agent_names()
    for md in sorted(CW_AGENTS.glob("*.md")):
        for ref in agent_skill_refs(md):
            if ref not in bundled_skills:
                problems.append(f"{md.relative_to(REPO)}: skills ref '{ref}' not bundled in cw/skills")
        _, fm, _ = split_frontmatter(md.read_text())
        if MARS_FRONTMATTER.search("".join(fm or [])):
            problems.append(f"{md.relative_to(REPO)}: Mars-only frontmatter key")
        m = CW_LEAKS.search(md.read_text())
        if m:
            problems.append(f"{md.relative_to(REPO)}: leaked Meridian vocab {m.group(0)!r}")

    # 6. Lint @agent references across all cw markdown (bodies, resources, descriptions).
    all_cw_md = sorted([*CW_SKILLS.rglob("*.md"), *CW_AGENTS.glob("*.md")])
    for md in all_cw_md:
        text = md.read_text()
        for ref in set(re.findall(r"@([a-z][a-z-]+)", text)):
            if ref not in agent_names and ref not in AT_ALLOWLIST:
                problems.append(f"{md.relative_to(REPO)}: @{ref} does not match a cw agent")

    # 7. Version consistency: marketplace.json and plugin.json must match mars.toml.
    # Auto-fixed in both modes — the version is purely derived, never
    # independently authored, so blocking on it just creates a chicken-and-egg
    # when `mars version patch` bumps mars.toml before the commit hook runs.
    mars_toml = REPO / "mars.toml"
    import json as _json
    mars_ver = None
    if mars_toml.is_file():
        for line in mars_toml.read_text().splitlines():
            m = re.match(r'^version\s*=\s*"(.+)"', line)
            if m:
                mars_ver = m.group(1)
                break

    # 7a. .claude-plugin/marketplace.json  metadata.version
    marketplace_json = REPO / ".claude-plugin" / "marketplace.json"
    if mars_ver and marketplace_json.is_file():
        mp = _json.loads(marketplace_json.read_text())
        mp_ver = mp.get("metadata", {}).get("version")
        if mp_ver and mars_ver != mp_ver:
            mp["metadata"]["version"] = mars_ver
            marketplace_json.write_text(_json.dumps(mp, indent=2) + "\n")
            subprocess.run(
                ["git", "add", str(marketplace_json)],
                cwd=REPO, capture_output=True,
            )
            notes.append(f"bumped marketplace.json version {mp_ver} → {mars_ver}")

    # 7b. cw/.claude-plugin/plugin.json  version
    plugin_json = REPO / "cw" / ".claude-plugin" / "plugin.json"
    if mars_ver and plugin_json.is_file():
        pj = _json.loads(plugin_json.read_text())
        pj_ver = pj.get("version")
        if pj_ver != mars_ver:
            pj["version"] = mars_ver
            plugin_json.write_text(_json.dumps(pj, indent=2) + "\n")
            subprocess.run(
                ["git", "add", str(plugin_json)],
                cwd=REPO, capture_output=True,
            )
            notes.append(f"bumped plugin.json version {pj_ver} → {mars_ver}")

    for n in notes:
        print(f"  · {n}")
    if problems:
        print(f"\n✗ {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    gen_s, man_s = len(GENERATED_SKILLS), len(MANUAL_SKILLS)
    gen_a, man_a = len(GENERATED_AGENTS), len(MANUAL_AGENTS)
    print(f"\n✓ cw distribution in sync"
          f" (skills: {gen_s} generated, {man_s} manual;"
          f" agents: {gen_a} generated, {man_a} manual);"
          f" no drift or leaks.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="sync GENERATED components from Mars .claude output")
    ap.add_argument("--lint", action="store_true", help="lint only (skip Mars build + drift check); use in CI")
    ap.add_argument("--list", action="store_true", help="print classification and exit")
    args = ap.parse_args()

    if args.list:
        print("GENERATED skills (copied from temp Mars consumer .claude/skills/):")
        for n in GENERATED_SKILLS:
            print(f"  {n}")
        print("\nMANUAL skills (linted only, never overwritten):")
        for n in MANUAL_SKILLS:
            print(f"  {n}")
        print(f"\nGENERATED agents (copied from temp Mars consumer .claude/agents/):")
        for n in GENERATED_AGENTS:
            print(f"  {n}")
        if MANUAL_AGENTS:
            print("\nMANUAL agents (linted only, never overwritten):")
            for n in MANUAL_AGENTS:
                print(f"  {n}")
        return 0

    mode = "Applying" if args.apply else "Linting" if args.lint else "Checking"
    print(f"{mode} cw distribution sync...")
    return run(apply=args.apply, lint_only=args.lint)


if __name__ == "__main__":
    sys.exit(main())
