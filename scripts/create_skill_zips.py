#!/usr/bin/env python3
"""
Create individual ZIP files for each skill in the creative-writing-skills directory.
These ZIPs are ready for users to upload to Claude.ai Skills.
"""

import os
import zipfile
import shutil
from pathlib import Path


def should_exclude(file_path: str) -> bool:
    """Check if a file should be excluded from the ZIP."""
    exclude_patterns = ['.DS_Store', '__pycache__', '.pyc', '.git']
    return any(pattern in file_path for pattern in exclude_patterns)


def create_skill_zip(skill_dir: Path, output_dir: Path) -> None:
    """Create a .skill file (ZIP format) for a single skill directory."""
    skill_name = skill_dir.name
    zip_path = output_dir / f"{skill_name}.skill"

    print(f"Creating {skill_name}.skill...")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the skill directory
        for root, dirs, files in os.walk(skill_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(d)]

            for file in files:
                if should_exclude(file):
                    continue

                file_path = Path(root) / file
                # Create archive name relative to skill directory
                arcname = skill_name / file_path.relative_to(skill_dir)
                zipf.write(file_path, arcname)

    print(f"  ✓ Created {zip_path.name} ({zip_path.stat().st_size // 1024} KB)")


def main():
    """Main function to create all skill ZIPs."""
    # Get repository root directory
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    skills_dir = repo_root / "creative-writing-skills"
    output_dir = repo_root / "zips"

    # Verify skills directory exists
    if not skills_dir.exists():
        print(f"Error: Skills directory not found at {skills_dir}")
        return

    # Clean and recreate output directory
    if output_dir.exists():
        print(f"Cleaning existing zips directory...")
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    print(f"\nCreating skill ZIPs in {output_dir}\n")

    # Find all skill directories (starting with 'cw-')
    skill_dirs = sorted([d for d in skills_dir.iterdir()
                        if d.is_dir() and d.name.startswith('cw-')])

    if not skill_dirs:
        print(f"Error: No skill directories found in {skills_dir}")
        return

    # Create ZIP for each skill
    for skill_dir in skill_dirs:
        create_skill_zip(skill_dir, output_dir)

    print(f"\n✓ Successfully created {len(skill_dirs)} .skill files in {output_dir}")
    print(f"\nSkill files:")
    for skill_file in sorted(output_dir.glob("*.skill")):
        print(f"  - {skill_file.name}")


if __name__ == "__main__":
    main()
