#!/usr/bin/env python3
"""
Build a document relationship map from markdown files.

Usage:
    uv run resources/graph.py [root_directory]
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path


MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MERMAID_REL_RE = re.compile(r"-->|---|-\.->|==>|--[^-]")
YAML_REF_KEYS = {
    "arc",
    "chapter",
    "characters",
    "location",
    "locations",
    "requires",
    "see",
    "related",
    "pov",
    "arc_id",
    "chapters",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a document relationship graph from markdown files."
    )
    parser.add_argument("root_directory", nargs="?", default=".")
    return parser.parse_args()


def iter_markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if ".git" not in path.parts and "node_modules" not in path.parts
    )


def split_frontmatter(text: str) -> tuple[list[str], list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], lines

    yaml_lines: list[str] = []
    body_start = 1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            body_start = idx + 1
            break
        yaml_lines.append(lines[idx])
    else:
        return [], lines

    return yaml_lines, lines[body_start:]


def extract_markdown_links(source: Path, body_lines: list[str]) -> list[tuple[Path, Path]]:
    body = "\n".join(body_lines)
    links: list[tuple[Path, Path]] = []
    for match in MARKDOWN_LINK_RE.finditer(body):
        target = match.group(1).strip().strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        resolved = (source.parent / target).resolve(strict=False)
        links.append((source, resolved))
    return links


def extract_wikilinks(source: Path, text: str) -> list[tuple[Path, str]]:
    return [(source, match.group(1).strip()) for match in WIKILINK_RE.finditer(text)]


def extract_mermaid_relationships(source: Path, lines: list[str]) -> list[tuple[Path, str]]:
    in_mermaid = False
    relationships: list[tuple[Path, str]] = []
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped.startswith("```mermaid"):
            in_mermaid = True
            continue
        if in_mermaid and stripped.startswith("```"):
            in_mermaid = False
            continue
        if in_mermaid and MERMAID_REL_RE.search(raw_line):
            relationships.append((source, stripped))
    return relationships


def extract_yaml_refs(source: Path, yaml_lines: list[str]) -> list[tuple[Path, str]]:
    refs: list[tuple[Path, str]] = []
    for line in yaml_lines:
        stripped = line.strip()
        if not stripped or ":" not in stripped:
            continue
        key = stripped.split(":", 1)[0].strip()
        if key in YAML_REF_KEYS:
            refs.append((source, stripped))
    return refs


def display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def main() -> int:
    args = parse_args()
    root = Path(args.root_directory).expanduser().resolve()
    if not root.exists():
        print(f"Root directory not found: {root}", file=sys.stderr)
        return 1

    markdown_files = iter_markdown_files(root)
    if not markdown_files:
        print(f"No .md files found under {root}")
        return 0

    links: list[tuple[Path, Path]] = []
    wikilinks: list[tuple[Path, str]] = []
    mermaid_relationships: list[tuple[Path, str]] = []
    yaml_refs: list[tuple[Path, str]] = []

    for path in markdown_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        yaml_lines, body_lines = split_frontmatter(text)
        links.extend(extract_markdown_links(path, body_lines))
        wikilinks.extend(extract_wikilinks(path, text))
        mermaid_relationships.extend(extract_mermaid_relationships(path, text.splitlines()))
        yaml_refs.extend(extract_yaml_refs(path, yaml_lines))

    link_pairs = sorted(links, key=lambda item: (display_path(item[0], root), str(item[1])))
    link_set = {(src, tgt) for src, tgt in link_pairs}
    linked_targets = {tgt for _, tgt in link_pairs}
    inbound_sources: dict[Path, set[Path]] = defaultdict(set)
    for src, tgt in link_pairs:
        inbound_sources[tgt].add(src)

    broken_links = [(src, tgt) for src, tgt in link_pairs if not tgt.exists()]
    orphaned = [path for path in markdown_files if path not in linked_targets]

    missing_backlinks: list[tuple[Path, Path]] = []
    for src, tgt in link_pairs:
        if tgt.exists() and (tgt, src) not in link_set:
            missing_backlinks.append((src, tgt))

    print("==========================================")
    print("  Document Relationship Graph")
    print(f"  Root: {root}")
    print(f"  Files: {len(markdown_files)} markdown files")
    print("==========================================")
    print()

    print("## Outbound Links")
    print()
    if link_pairs:
        for src, tgt in link_pairs:
            print(f"{display_path(src, root)} -> {display_path(tgt, root)}")
    else:
        print("(no markdown links found)")
    print()

    print("## Wikilink Entity Mentions")
    print()
    if wikilinks:
        by_entity: dict[str, list[str]] = defaultdict(list)
        for src, entity in wikilinks:
            by_entity[entity].append(display_path(src, root))
        for entity in sorted(by_entity):
            print(f"[[{entity}]]:")
            for src in sorted(by_entity[entity]):
                print(f"  - {src}")
            print()
    else:
        print("(no wikilinks found)")
        print()

    print("## Mermaid Relationships")
    print()
    if mermaid_relationships:
        for src, relation in sorted(
            mermaid_relationships,
            key=lambda item: (display_path(item[0], root), item[1]),
        ):
            print(f"{display_path(src, root)}: {relation}")
    else:
        print("(no mermaid relationships found)")
    print()

    print("## YAML Front Matter References")
    print()
    if yaml_refs:
        for src, ref in sorted(
            yaml_refs, key=lambda item: (display_path(item[0], root), item[1])
        ):
            print(f"{display_path(src, root)}: {ref}")
    else:
        print("(no YAML references found)")
    print()

    print("## Broken Links")
    print()
    if broken_links:
        for src, tgt in broken_links:
            print(f"  {display_path(src, root)} -> {display_path(tgt, root)} (not found)")
    else:
        print("(no broken links)")
    print()

    print("## Orphaned Files (no inbound links)")
    print()
    if orphaned:
        for path in orphaned:
            print(f"  {display_path(path, root)}")
    else:
        print("(no orphaned files)")
    print()

    print("## Missing Back-links (A -> B but B does not -> A)")
    print()
    if missing_backlinks:
        for src, tgt in missing_backlinks:
            print(
                f"  {display_path(src, root)} -> {display_path(tgt, root)} (no back-link)"
            )
    else:
        print("(no missing back-links)")
    print()

    print("## Summary")
    print(f"  Files scanned:       {len(markdown_files)}")
    print(f"  Markdown links:      {len(link_pairs)}")
    print(f"  Wikilinks:           {len(wikilinks)}")
    print(f"  Mermaid relations:   {len(mermaid_relationships)}")
    print(f"  Broken links:        {len(broken_links)}")
    print(f"  Orphaned files:      {len(orphaned)}")
    print(f"  Missing back-links:  {len(missing_backlinks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
