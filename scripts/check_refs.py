#!/usr/bin/env python3
"""Fail when the built plugin tree points at an agent or skill it does not ship.

`mars build plugin` drops prose references to items a dependency's include
filter leaves out, and neither `mars check` nor `claude plugins validate`
reads them: a skill can ship telling an agent to load `/grill` or spawn
`@explorer` while neither exists in the tree. This scans the lowered Claude
tree for those references and lists the ones that do not resolve.

Usage:
    python3 scripts/check_refs.py

It reads the committed `plugin/claude` tree, so run `mars build plugin` first.

Reference forms recognized:

    @agent           prose delegation
    <pkg>:<skill>    namespaced skill, backticked or bare. Mars rewrites every
                     skill reference it lowers to this form, including the
                     `skills:` entries at the top of an agent file.
    `/skill`         backticked bare skill

A bare `/name` is only read as a skill when it is backticked: an unbackticked
slash in this tree is a file path (`/external/drive.yaml`) far more often than
it is a skill. `<pkg>` must be this plugin's name, which is what Mars rewrites
references to; other `word:word` text (DOI prefixes, CSS values) is not a
skill reference.

Exit status is 0 when every reference resolves, 1 with the dangling ones
listed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TREE = REPO / "plugin" / "claude"

# `@name` that is not an agent reference: package scopes in imports
# (`@xyflow/react`) and the install spec naming this package.
NON_AGENT_AT = {"xyflow", "creative-writing-skills"}

AT_REF = re.compile(r"(?<![A-Za-z0-9_@.-])@([a-z][a-z0-9-]*)")
NAMESPACED = re.compile(
    r"(?<![A-Za-z0-9_-])([a-z][a-z0-9-]*):([a-z0-9][a-z0-9-]*)(?![A-Za-z0-9_-])"
)
BARE_SKILL = re.compile(r"`/([a-z][a-z0-9-]*)`")


def main() -> int:
    package = json.loads((TREE / ".claude-plugin" / "plugin.json").read_text())["name"]
    agents = {path.stem for path in (TREE / "agents").glob("*.md")}
    skills = {path.parent.name for path in (TREE / "skills").glob("*/SKILL.md")}

    dangling: list[str] = []
    for path in sorted(TREE.rglob("*.md")):
        where = str(path.relative_to(TREE))
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            at = f"{where}:{lineno}"

            for match in AT_REF.finditer(line):
                name = match.group(1)
                if name not in agents and name not in NON_AGENT_AT:
                    dangling.append(f"{at}: @{name} is not a shipped agent")

            for match in NAMESPACED.finditer(line):
                # Agents and skills share the plugin namespace, so a
                # namespaced name resolves against either.
                if match.group(1) == package and not (
                    match.group(2) in skills or match.group(2) in agents
                ):
                    dangling.append(f"{at}: {match.group(0)} is not a shipped item")

            for match in BARE_SKILL.finditer(line):
                if match.group(1) not in skills:
                    dangling.append(f"{at}: `{match.group(0)[1:-1]}` is not a shipped skill")

    if dangling:
        for entry in dangling:
            print(entry)
        print(
            f"\ncheck_refs: {len(dangling)} dangling reference(s) in {TREE.relative_to(REPO)}. "
            "Widen the include list in mars.toml, or delete the reference.",
            file=sys.stderr,
        )
        return 1

    print(f"check_refs: every reference resolves ({len(agents)} agents, {len(skills)} skills).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
