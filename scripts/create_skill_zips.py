#!/usr/bin/env python3
"""
Create `.skill` ZIP files for Claude.ai uploads.

Sources:
- `cw/skills/*`

Each archive is rooted at the skill directory name and contains:
- `SKILL.md`
- `resources/` (if present)
"""

import shutil
import zipfile
from pathlib import Path


EXCLUDED_PARTS = {".DS_Store", "__pycache__", ".git"}
EXCLUDED_SUFFIXES = {".pyc"}


def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from an archive."""
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return True
    if path.name in EXCLUDED_PARTS:
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return True
    return False


def find_skill_dirs(repo_root: Path) -> list[Path]:
    """Find skills under `cw/skills/*`."""
    skills_root = repo_root / "cw" / "skills"

    skill_dirs = []
    if skills_root.exists():
        skill_dirs.extend(sorted(d for d in skills_root.iterdir() if d.is_dir()))

    return skill_dirs


def iter_skill_files(skill_dir: Path) -> list[Path]:
    """Return files to include for one skill (SKILL.md + resources)."""
    files: list[Path] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"Missing SKILL.md in {skill_dir}")
    files.append(skill_md)

    resources_dir = skill_dir / "resources"
    if resources_dir.is_dir():
        for file_path in sorted(resources_dir.rglob("*")):
            if not file_path.is_file():
                continue
            if should_exclude(file_path.relative_to(skill_dir)):
                continue
            files.append(file_path)

    return files


def create_skill_zip(skill_dir: Path, output_dir: Path) -> None:
    """Create a .skill file (ZIP format) for a single skill directory."""
    skill_name = skill_dir.name
    zip_path = output_dir / f"{skill_name}.skill"

    print(f"Creating {skill_name}.skill...")

    files = iter_skill_files(skill_dir)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files:
            arcname = Path(skill_name) / file_path.relative_to(skill_dir)
            zipf.write(file_path, str(arcname))

    print(f"  ✓ Created {zip_path.name} ({zip_path.stat().st_size // 1024} KB)")


def main() -> int:
    """Main function to create all skill ZIPs."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    output_dir = repo_root / "zips"

    if output_dir.exists():
        print(f"Cleaning existing zips directory...")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nCreating skill ZIPs in {output_dir}\n")

    skill_dirs = find_skill_dirs(repo_root)

    if not skill_dirs:
        print("Error: No skill directories found under cw/skills")
        return 1

    for skill_dir in skill_dirs:
        create_skill_zip(skill_dir, output_dir)

    print(f"\n✓ Successfully created {len(skill_dirs)} .skill files in {output_dir}")
    print(f"\nSkill files:")
    for skill_file in sorted(output_dir.glob("*.skill")):
        print(f"  - {skill_file.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
