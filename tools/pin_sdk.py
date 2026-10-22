#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/pin_sdk.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Pin every consumer of this SDK to one released tag.

A consumer names the SDK in two places: the dependency line of its
`pyproject.toml` (`hydra-umc-sdk @ git+https://github.com/JuanenRac/HYDRA-UMC-SDK.git@<ref>#...`)
and, for the repositories that check the contract fixtures out in CI, the
`ref:` next to `repository: JuanenRac/HYDRA-UMC-SDK` in `.github/workflows/ci.yml`.
A branch name or a bare commit there means a change of the SDK can break a
consumer without anyone touching it. This script rewrites both to a tag.

    python tools/pin_sdk.py --check            # list every reference not on the tag, exit 1 if any
    python tools/pin_sdk.py                    # rewrite them to the newest tag of this checkout
    python tools/pin_sdk.py --tag v0.3.4       # rewrite them to a given tag

The newest tag is read from this checkout (`git tag`), so release the SDK first,
then pin. Only references to the SDK are touched.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parents[1]
TAG_PATTERN = re.compile(r"^v\d+\.\d+\.\d+(?:\.\d+)?$")

# `...HYDRA-UMC-SDK.git@<ref>#subdirectory=...` in pyproject.toml / requirements files
_DEPENDENCY = re.compile(r"(HYDRA-UMC-SDK\.git@)([^#\s\"']+)")
# `repository: JuanenRac/HYDRA-UMC-SDK, ... ref: <ref>` on one line, or a `ref:` on the next line(s)
_WORKFLOW_INLINE = re.compile(r"(repository:\s*JuanenRac/HYDRA-UMC-SDK\b[^\n}]*?\bref:\s*)([^\s,}]+)")
_WORKFLOW_BLOCK = re.compile(r"(repository:\s*JuanenRac/HYDRA-UMC-SDK[ \t]*\r?\n(?:[ \t]+[^\n]*\r?\n)*?[ \t]+ref:\s*)([^\s#]+)")

SCANNED = ("pyproject.toml", "requirements.txt", "requirements-dev.txt", ".github/workflows/ci.yml")


def newest_tag(sdk_root: Path = SDK_ROOT) -> str:
    result = subprocess.run(["git", "tag", "--list", "v*"], cwd=sdk_root, capture_output=True, text=True, check=True)
    tags = [t for t in result.stdout.split() if TAG_PATTERN.match(t)]
    if not tags:
        raise SystemExit("this checkout has no release tag")
    return max(tags, key=lambda tag: tuple(int(part) for part in tag[1:].split(".")))


def repin(text: str, tag: str) -> tuple[str, list[str]]:
    """Return the text with every SDK reference on `tag`, and the refs that were replaced."""
    replaced: list[str] = []

    def swap(match: re.Match[str]) -> str:
        if match.group(2) != tag:
            replaced.append(match.group(2))
        return match.group(1) + tag

    for pattern in (_DEPENDENCY, _WORKFLOW_INLINE, _WORKFLOW_BLOCK):
        text = pattern.sub(swap, text)
    return text, replaced


def consumers(workspace: Path) -> list[Path]:
    found = []
    for repo in sorted(workspace.iterdir()):
        if repo.is_dir() and (repo.name == "HYDRA-UMC" or repo.name.startswith("HYDRA-UMC-")) and repo.name != "HYDRA-UMC-SDK":
            found.append(repo)
    return found


def process(workspace: Path, tag: str, write: bool) -> list[tuple[str, list[str]]]:
    changes: list[tuple[str, list[str]]] = []
    for repo in consumers(workspace):
        for relative in SCANNED:
            path = repo / relative
            if not path.is_file():
                continue
            raw = path.read_bytes().decode("utf-8")
            new, replaced = repin(raw, tag)
            if not replaced:
                continue
            changes.append((f"{repo.name}/{relative}", replaced))
            if write:
                path.write_bytes(new.encode("utf-8"))
    return changes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 if a reference is not on the tag")
    parser.add_argument("--tag", help="tag to pin to (default: the newest tag of this checkout)")
    parser.add_argument("--workspace", type=Path, default=SDK_ROOT.parent)
    args = parser.parse_args(argv)
    tag = args.tag or newest_tag()
    if not TAG_PATTERN.match(tag):
        print(f"not a release tag: {tag}", file=sys.stderr)
        return 2
    changes = process(args.workspace.resolve(), tag, write=not args.check)
    for where, refs in changes:
        print(("not on " if args.check else "pinned to ") + f"{tag}: {where} (was {', '.join(refs)})")
    verdict = "FAIL" if (args.check and changes) else "PASS"
    print(f"SDK_PIN={verdict} tag={tag} references={len(changes)}")
    return 1 if (args.check and changes) else 0


if __name__ == "__main__":
    raise SystemExit(main())
