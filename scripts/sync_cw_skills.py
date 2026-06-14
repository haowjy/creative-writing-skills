#!/usr/bin/env python3
"""
Sync the generalizable `cw/` skills from canonical source and lint the cw
distribution for drift and leaked Meridian vocabulary.

`cw/skills/` splits into two kinds:

  MIRROR  Pure-craft skills with no harness-specific content. Auto-synced
          verbatim from `skills/<name>/` (body + resources/), with frontmatter
          rewritten to Claude vocab (`name` + `description`). Run with --apply
          to update them; --check fails if cw has drifted from source.

  MANUAL  Skills that carry Meridian->generic adaptations (spawn mechanics,
          env paths), come from the meridian-base dependency, or are cw-only.
          The tool never overwrites these; it only lints them.

Usage:
  python scripts/sync_cw_skills.py            # check mode (CI gate); exit 1 on problems
  python scripts/sync_cw_skills.py --apply    # sync MIRROR skills from source
  python scripts/sync_cw_skills.py --list     # print the classification and exit
"""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SRC_SKILLS = REPO / "skills"
CW_SKILLS = REPO / "cw" / "skills"
CW_AGENTS = REPO / "cw" / "agents"

# --- Classification -------------------------------------------------------
# Pure-craft skills mirrored verbatim from skills/<name>/. Keep this list in
# sync with reality: a skill belongs here only if its source carries zero
# Meridian-specific content (the guard below enforces this).
MIRROR = [
    "brainstorming",
    "prose-critique",
    "prose-writing",
    "scene-construction",
    "story-architecture",
    "style-analysis",
    "writing-issues",
    "writing-principles",
]

# Hand-maintained cw skills the tool lints but never overwrites.
MANUAL = [
    # local skills carrying Meridian->generic adaptations
    "story-context",
    "writing-artifacts",
    "writing-staffing",
    # adapted from the meridian-base dependency (source is gitignored .mars/)
    "llm-writing",
    "shared-dao",
    "intent-modeling",
    "grill-with-docs",
    # cw-only, no upstream
    "cw-muse",
    "kb-management",
    "project-setup",
]

# --- Patterns -------------------------------------------------------------
# Content that must never appear in a MIRROR source (would mean it is no longer
# a clean mirror and should be reclassified to MANUAL + genericized).
MERIDIAN_IN_SOURCE = re.compile(
    r"\bmeridian\b|\$MERIDIAN|\bmeridian spawn\b|--from\b|/meridian-spawn"
    r"|@(?:bard|lore-keeper|explorer|web-researcher|kb-writer|kb-maintainer|session-\w+)",
    re.IGNORECASE,
)

# Vocabulary that should never leak into any cw file (command/env/infra refs).
CW_LEAKS = re.compile(
    r"\bmeridian spawn\b|\$?MERIDIAN_[A-Z_]+|--from\b|/meridian-spawn|/qi-layer"
    r"|/knowledge-layers|/md-validation|\.context/CONTEXT|deny_headless"
    r"|@(?:bard|lore-keeper|explorer|web-researcher|kb-writer|kb-maintainer|session-\w+)",
)

# Mars-only frontmatter keys (cw must use Claude vocab: name + description).
MARS_FRONTMATTER = re.compile(r"^(type|model-invocable|effort|model-policies|sandbox):", re.M)


# --- Frontmatter helpers --------------------------------------------------
def split_frontmatter(text: str):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[:1], lines[1:i], lines[i:]
    return None, None, text


def to_claude_frontmatter(src_text: str, name: str) -> str:
    """Keep description, drop Mars-only keys, force name = dir."""
    open_, fm, rest = split_frontmatter(src_text)
    if fm is None:
        return src_text
    kept, skipping = [], False
    for line in fm:
        top_level = line[:1] not in (" ", "\t")
        if top_level:
            skipping = line.lstrip().startswith(
                ("name:", "type:", "model-invocable:", "effort:")
            )
        if not skipping:
            kept.append(line)
    return "".join(open_) + f"name: {name}\n" + "".join(kept) + "".join(rest)


def body_of(path: pathlib.Path) -> str:
    _, _, rest = split_frontmatter(path.read_text())
    return "".join(rest) if isinstance(rest, list) else rest


# --- Operations -----------------------------------------------------------
def mirror_skill(name: str) -> bool:
    """Copy source SKILL.md (Claude frontmatter) + resources/ into cw. Returns changed."""
    src_dir, cw_dir = SRC_SKILLS / name, CW_SKILLS / name
    cw_dir.mkdir(parents=True, exist_ok=True)
    changed = False

    new_md = to_claude_frontmatter((src_dir / "SKILL.md").read_text(), name)
    cw_md = cw_dir / "SKILL.md"
    if not cw_md.exists() or cw_md.read_text() != new_md:
        cw_md.write_text(new_md)
        changed = True

    src_res, cw_res = src_dir / "resources", cw_dir / "resources"
    if src_res.is_dir():
        if not cw_res.is_dir() or _dir_differs(src_res, cw_res):
            if cw_res.exists():
                shutil.rmtree(cw_res)
            shutil.copytree(src_res, cw_res)
            changed = True
    elif cw_res.exists():
        shutil.rmtree(cw_res)
        changed = True
    return changed


def _dir_differs(a: pathlib.Path, b: pathlib.Path) -> bool:
    af = {p.relative_to(a): p for p in a.rglob("*") if p.is_file()}
    bf = {p.relative_to(b): p for p in b.rglob("*") if p.is_file()}
    if set(af) != set(bf):
        return True
    return any(af[k].read_bytes() != bf[k].read_bytes() for k in af)


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


# --- Checks ---------------------------------------------------------------
def run(apply: bool) -> int:
    problems: list[str] = []
    notes: list[str] = []

    # 0. Classification completeness: every cw skill must be classified.
    classified = set(MIRROR) | set(MANUAL)
    bundled = bundled_skill_names()
    for unknown in sorted(bundled - classified):
        problems.append(f"cw/skills/{unknown} is unclassified — add it to MIRROR or MANUAL")
    for missing in sorted(classified - bundled):
        problems.append(f"{missing} is classified but missing from cw/skills/")

    # 1. Guard: MIRROR sources must be Meridian-free.
    for name in MIRROR:
        src = SRC_SKILLS / name
        if not src.is_dir():
            problems.append(f"MIRROR skill {name} has no source at skills/{name}/")
            continue
        hits = [
            f"{p.relative_to(REPO)}: {m.group(0)!r}"
            for p in src.rglob("*.md")
            for m in [MERIDIAN_IN_SOURCE.search(p.read_text())]
            if m
        ]
        if hits:
            problems.append(
                f"MIRROR skill {name} source has Meridian content — reclassify to MANUAL "
                f"and genericize:\n      " + "\n      ".join(hits)
            )

    # 2. Sync or drift-check MIRROR skills.
    for name in MIRROR:
        if not (SRC_SKILLS / name).is_dir():
            continue
        if apply:
            if mirror_skill(name):
                notes.append(f"synced {name}")
        else:
            cw_md = CW_SKILLS / name / "SKILL.md"
            if not cw_md.exists():
                problems.append(f"{name}: cw/skills/{name}/SKILL.md missing (run --apply)")
                continue
            if body_of(SRC_SKILLS / name / "SKILL.md") != body_of(cw_md):
                problems.append(f"{name}: cw body has drifted from source (run --apply)")
            sr, cr = SRC_SKILLS / name / "resources", CW_SKILLS / name / "resources"
            if sr.is_dir() and (not cr.is_dir() or _dir_differs(sr, cr)):
                problems.append(f"{name}: resources/ drifted from source (run --apply)")

    # 3. Lint all cw skills: Claude frontmatter, no leaks.
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

    # 5. Lint @agent references across cw bodies.
    for md in sorted([*CW_SKILLS.glob("*/SKILL.md"), *CW_AGENTS.glob("*.md")]):
        for ref in set(re.findall(r"@([a-z][a-z-]+)", body_of(md))):
            if ref not in agent_names and ref not in {"anthropic"}:
                notes.append(f"{md.relative_to(REPO)}: @{ref} does not match a cw agent (review)")

    # --- Report ---
    for n in notes:
        print(f"  · {n}")
    if problems:
        print(f"\n✗ {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"\n✓ cw skills in sync ({len(MIRROR)} mirrored, {len(MANUAL)} manual); no drift or leaks.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="sync MIRROR skills from source")
    ap.add_argument("--list", action="store_true", help="print classification and exit")
    args = ap.parse_args()

    if args.list:
        print("MIRROR (auto-synced from skills/<name>/):")
        for n in MIRROR:
            print(f"  {n}")
        print("\nMANUAL (linted only, never overwritten):")
        for n in MANUAL:
            print(f"  {n}")
        return 0

    print(f"{'Applying' if args.apply else 'Checking'} cw skill sync...")
    return run(apply=args.apply)


if __name__ == "__main__":
    sys.exit(main())
