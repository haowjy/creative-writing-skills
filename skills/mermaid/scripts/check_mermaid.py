#!/usr/bin/env python3
"""Validate Mermaid diagrams in Markdown using Mermaid CLI."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

NODE_VERSION = "22.11.0"


def run_setup(command: list[str], **kwargs: object) -> None:
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        **kwargs,
    )
    if result.returncode == 0:
        return
    if result.stdout:
        print(result.stdout, file=sys.stderr)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    raise subprocess.CalledProcessError(result.returncode, command)


def iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return [
            file
            for file in path.rglob("*.md")
            if ".git" not in file.parts and "node_modules" not in file.parts
        ]
    print(f"WARN: skipping {path} (not found)", file=sys.stderr)
    return []


def extract_blocks(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".mmd":
        return [(1, text)]

    blocks: list[tuple[int, str]] = []
    in_block = False
    start_line = 0
    current: list[str] = []

    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not in_block and stripped.startswith("```mermaid"):
            in_block = True
            start_line = line_no
            current = []
            continue
        if in_block and stripped.startswith("```"):
            blocks.append((start_line, "\n".join(current) + "\n"))
            in_block = False
            continue
        if in_block:
            current.append(line)

    return blocks


def executable(name: str) -> str | None:
    if os.name == "nt":
        return shutil.which(f"{name}.cmd") or shutil.which(name)
    return shutil.which(name)


def cache_root() -> Path:
    override = os.environ.get("MERMAID_VALIDATOR_CACHE")
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "creative-writing-skills" / "mermaid-validator"
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "creative-writing-skills" / "mermaid-validator"


def cached_npx(node_dir: Path) -> str | None:
    candidates = [
        node_dir / "bin" / "npx",
        node_dir / "bin" / "npx.cmd",
        node_dir / "Scripts" / "npx",
        node_dir / "Scripts" / "npx.cmd",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def ensure_nodeenv_python(root: Path) -> Path:
    venv_dir = root / "venv"
    python = venv_python(venv_dir)
    if python.exists():
        return python

    uv = executable("uv")
    if uv:
        run_setup([uv, "venv", "--quiet", str(venv_dir)])
        run_setup(
            [uv, "pip", "install", "--quiet", "--python", str(python), "nodeenv"],
        )
        return python

    run_setup([sys.executable, "-m", "venv", str(venv_dir)])
    run_setup([str(python), "-m", "pip", "install", "--quiet", "nodeenv"])
    return python


def bootstrap_npx() -> str | None:
    if os.environ.get("MERMAID_VALIDATOR_NO_BOOTSTRAP"):
        return None

    root = cache_root()
    node_dir = root / f"node-v{NODE_VERSION}"
    existing = cached_npx(node_dir)
    if existing:
        return existing

    print(
        f"Mermaid validation needs Node.js/npm. None was found, so this script "
        f"will install a private Node {NODE_VERSION} runtime in {root}. "
        "This is a one-time download and does not modify the repo or system Node.",
        file=sys.stderr,
    )

    python = ensure_nodeenv_python(root)
    run_setup(
        [str(python), "-m", "nodeenv", "--quiet", f"--node={NODE_VERSION}", "--force", str(node_dir)],
    )
    return cached_npx(node_dir)


def get_npx() -> str | None:
    return executable("npx") or bootstrap_npx()


def node_env(npx: str) -> dict[str, str]:
    env = os.environ.copy()
    npx_dir = str(Path(npx).parent)
    env["PATH"] = npx_dir if not env.get("PATH") else npx_dir + os.pathsep + env["PATH"]
    return env


def validate_block(npx: str, text: str, tmp: Path) -> tuple[bool, str]:
    source = tmp / "diagram.mmd"
    output = tmp / "diagram.svg"
    source.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [npx, "--yes", "@mermaid-js/mermaid-cli", "-q", "-i", str(source), "-o", str(output)],
        env=node_env(npx),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        return True, ""

    error = "\n".join(
        line for line in result.stderr.splitlines() if not line.lower().startswith("npm warn")
    )
    return False, error.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    npx = get_npx()
    if npx is None:
        print(
            "ERROR: Mermaid validation needs Node.js/npm. Automatic bootstrap "
            "was disabled or failed. Install Node.js from https://nodejs.org/ "
            "or unset MERMAID_VALIDATOR_NO_BOOTSTRAP. If no Python, uv, mise, "
            "or Node runtime is available, ask the user before installing one.",
            file=sys.stderr,
        )
        return 2

    files: list[Path] = []
    for target in args.paths:
        files.extend(iter_files(target))

    total = 0
    failed = 0

    with tempfile.TemporaryDirectory(prefix="mermaid-check-") as tmp_name:
        tmp = Path(tmp_name)
        for file in files:
            for line, block in extract_blocks(file):
                total += 1
                ok, error = validate_block(npx, block, tmp)
                if ok:
                    continue
                failed += 1
                print(f"FAIL: {file}:{line}", file=sys.stderr)
                if error:
                    print(error, file=sys.stderr)

    if total == 0:
        print("No Mermaid diagrams found.")
        return 0

    print(f"Mermaid diagrams: {total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
