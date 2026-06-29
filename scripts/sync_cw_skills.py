#!/usr/bin/env python3
"""
Build and lint the `cw/` Claude/plugin skill distribution.

`cw/skills/` splits into two kinds:

  GENERATED  Copied from a temporary Mars consumer project's `.claude/skills/`.
             Mars performs the harness lowering; this script only filters the
             skills that belong in the cw distribution. Run with --apply to
             refresh them; check mode fails on drift.

  MANUAL     cw-only or cw-adapted skills. Some dependency skills are manual
             because their Mars output contains Meridian-specific vocabulary.
             The tool never overwrites these; it only lints them.

Usage:
  python scripts/sync_cw_skills.py            # check mode; exit 1 on problems
  python scripts/sync_cw_skills.py --apply    # run Mars sync + refresh GENERATED skills
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

# Skills shipped in the cw distribution from Mars-lowered `.claude/skills/`.
# Keep this filtered: dependency packages contain many operational skills that
# do not belong in a creative-writing plugin.
GENERATED = [
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
    "intent-modeling",
    "interactive-artifact",
    "llm-writing",
]

# Hand-maintained cw-only skills the tool lints but never overwrites.
MANUAL = [
    # local skills carrying cw-specific adaptations
    "writing-staffing",
    # dependency skills that need cw-specific de-Meridianization
    "grill-with-docs",
    "shared-dao",
    # cw-only, no upstream Mars source
    "kb-management",
    "project-setup",
]

# Vocabulary that should never leak into any cw file (command/env/infra refs).
CW_LEAKS = re.compile(
    r"\bmeridian spawn\b|\$?MERIDIAN_[A-Z_]+|--from\b|/meridian-spawn|/qi-layer"
    r"|/knowledge-layers|/md-validation|\.context/CONTEXT|deny_headless"
    r"|@(?:bard|lore-keeper|explorer|kb-writer|kb-maintainer|session-\w+)",
)

# Mars-only frontmatter keys (cw must use Claude vocab: name + description).
MARS_FRONTMATTER = re.compile(r"^(type|model-invocable|effort|model-policies|sandbox):", re.M)


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


def build_claude_skills() -> pathlib.Path:
    """Return a temp `.claude/skills` built from this package as a dependency."""
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
    return tmp / ".claude" / "skills"


def bundled_skill_names() -> set[str]:
    return {d.name for d in CW_SKILLS.iterdir() if d.is_dir()}


def agent_skill_refs(path: pathlib.Path) -> list[str]:
    """Parse the `skills:` block of an agent, ignoring prose like descriptions."""
    _, fm, _ = split_frontmatter(path.read_text())
    if fm is None:
        return []
    refs, in_block = [], False
    for line in fm:
        if re.match(r"^skills:", line):
            in_block = True
            continue
        if in_block:
            m = re.match(r"\s*-\s*creative-writing-skills:([a-z0-9-]+)", line)
            if m:
                refs.append(m.group(1))
            elif line[:1] not in (" ", "\t", "\n", ""):
                break
    return refs


def run(apply: bool) -> int:
    problems: list[str] = []
    notes: list[str] = []

    generated_root: pathlib.Path | None = None
    try:
        generated_root = build_claude_skills()
    except Exception as exc:
        problems.append(str(exc))

    # 1. Sync or drift-check GENERATED skills from temp Mars .claude output.
    if generated_root is not None:
        for name in GENERATED:
            src_dir = generated_root / name
            cw_dir = CW_SKILLS / name
            if not src_dir.is_dir():
                problems.append(f"GENERATED skill {name} missing from Mars .claude/skills output")
                continue
            if apply:
                if copy_skill_dir(src_dir, cw_dir):
                    notes.append(f"synced {name}")
            else:
                if not cw_dir.is_dir():
                    problems.append(f"{name}: cw/skills/{name}/ missing (run --apply)")
                    continue
                if _dir_differs(src_dir, cw_dir):
                    problems.append(f"{name}: cw skill dir drifted from Mars .claude output (run --apply)")

    # 2. Classification completeness: every cw skill must be classified.
    classified = set(GENERATED) | set(MANUAL)
    bundled = bundled_skill_names()
    for unknown in sorted(bundled - classified):
        problems.append(f"cw/skills/{unknown} is unclassified — add it to GENERATED or MANUAL")
    for missing in sorted(classified - bundled):
        problems.append(f"{missing} is classified but missing from cw/skills/")

    # 3. Lint all cw skills: Claude frontmatter, no leaks (SKILL.md + resources).
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

    # 4. Lint cw agents: skills refs resolve, no leaks, Claude frontmatter.
    agent_names = {p.stem for p in CW_AGENTS.glob("*.md")}
    for md in sorted(CW_AGENTS.glob("*.md")):
        for ref in agent_skill_refs(md):
            if ref not in bundled:
                problems.append(f"{md.relative_to(REPO)}: skills ref '{ref}' not bundled in cw/skills")
        _, fm, _ = split_frontmatter(md.read_text())
        if MARS_FRONTMATTER.search("".join(fm or [])):
            problems.append(f"{md.relative_to(REPO)}: Mars-only frontmatter key")
        m = CW_LEAKS.search(md.read_text())
        if m:
            problems.append(f"{md.relative_to(REPO)}: leaked Meridian vocab {m.group(0)!r}")

    # 5. Lint @agent references across all cw markdown (bodies, resources, descriptions).
    all_cw_md = sorted([*CW_SKILLS.rglob("*.md"), *CW_AGENTS.glob("*.md")])
    for md in all_cw_md:
        text = md.read_text()
        for ref in set(re.findall(r"@([a-z][a-z-]+)", text)):
            if ref not in agent_names and ref not in {"anthropic", "kb-lead"}:
                problems.append(f"{md.relative_to(REPO)}: @{ref} does not match a cw agent")

    for n in notes:
        print(f"  · {n}")
    if problems:
        print(f"\n✗ {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"\n✓ cw skills in sync ({len(GENERATED)} generated, {len(MANUAL)} manual); no drift or leaks.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="sync GENERATED skills from Mars .claude output")
    ap.add_argument("--list", action="store_true", help="print classification and exit")
    args = ap.parse_args()

    if args.list:
        print("GENERATED (copied from temp Mars consumer .claude/skills/):")
        for n in GENERATED:
            print(f"  {n}")
        print("\nMANUAL (linted only, never overwritten):")
        for n in MANUAL:
            print(f"  {n}")
        return 0

    print(f"{'Applying' if args.apply else 'Checking'} cw skill sync...")
    return run(apply=args.apply)


if __name__ == "__main__":
    sys.exit(main())
