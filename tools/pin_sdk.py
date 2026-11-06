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
The same goes for every other workflow of a consumer (`sitl.yml`, `install-smoke.yml`, ...,
including a `repository:` whose owner is `${{ github.repository_owner }}`), for a dependency
installed from the release tarball (`.../HYDRA-UMC-SDK/archive/refs/tags/<tag>.tar.gz`), for the
`ref:` of a Flutter `git:` dependency in `pubspec.yaml` and for the `ref` / `resolved-ref` pair of
`pubspec.lock` (the lock records the commit of the tag, read from this checkout).

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
# The owner may be spelled out or come from the workflow context (`${{ github.repository_owner }}`).
_OWNER = r"(?:JuanenRac|\$\{\{[^}\r\n]*\}\})"
_WORKFLOW_INLINE = re.compile(r"(repository:\s*" + _OWNER + r"/HYDRA-UMC-SDK\b[^\n}]*?\bref:\s*)([^\s,}]+)")
_WORKFLOW_BLOCK = re.compile(r"(repository:\s*" + _OWNER + r"/HYDRA-UMC-SDK[ \t]*\r?\n(?:[ \t][^\r\n]*\r?\n)*?[ \t]+ref:\s*)([^\s#]+)")
# `.../HYDRA-UMC-SDK/archive/refs/tags/<tag>.tar.gz` (a dependency installed from the release tarball)
_TARBALL = re.compile(r"(HYDRA-UMC-SDK/archive/refs/tags/)(v\d+\.\d+\.\d+(?:\.\d+)?)(\.(?:tar\.gz|zip))")
# a Flutter `git:` dependency in pubspec.yaml: the `url:` line, then the `ref:` of the same block
# (the `ref:` has to sit at the indentation of the `url:` line, so it can never be the one of the next dependency)
_PUBSPEC = re.compile(
    r"^(?P<ind>[ \t]+)(?P<head>url:\s*\"?https://github\.com/JuanenRac/HYDRA-UMC-SDK\.git\"?[ \t]*\r?\n"
    r"(?:(?P=ind)(?!ref:)[^\r\n]*\r?\n)*?(?P=ind)ref:\s*)(?P<ref>[^\s#\"']+)",
    re.MULTILINE,
)
# the same dependency in pubspec.lock: `ref:` and `resolved-ref:` come before the `url:` line
_LOCK = re.compile(
    r"(\bref:\s*)(\"?)([^\s\"]+)(\"?)(\r?\n[ \t]+resolved-ref:\s*)(\"?)([^\s\"]+)(\"?)"
    r"(\r?\n[ \t]+url:\s*\"?https://github\.com/JuanenRac/HYDRA-UMC-SDK\.git)"
)

SCANNED = ("pyproject.toml", "requirements.txt", "requirements-dev.txt", "pubspec.yaml", "pubspec.lock")
WORKFLOWS = ".github/workflows"


def newest_tag(sdk_root: Path = SDK_ROOT) -> str:
    result = subprocess.run(["git", "tag", "--list", "v*"], cwd=sdk_root, capture_output=True, text=True, check=True)
    tags = [t for t in result.stdout.split() if TAG_PATTERN.match(t)]
    if not tags:
        raise SystemExit("this checkout has no release tag")
    return max(tags, key=lambda tag: tuple(int(part) for part in tag[1:].split(".")))


def tag_commit(tag: str, sdk_root: Path = SDK_ROOT) -> str | None:
    """The commit a tag of this checkout points at (what a lock file records), or None."""
    result = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{tag}^{{commit}}"], cwd=sdk_root, capture_output=True, text=True, check=False)
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", sha) else None


def repin(text: str, tag: str, commit: str | None = None) -> tuple[str, list[str]]:
    """Return the text with every SDK reference on `tag`, and the refs that were replaced.

    `commit` is the commit of the tag; a pubspec.lock records it as `resolved-ref`, so
    without it a lock file is left alone (a lock whose `ref` and `resolved-ref` disagree
    would make `flutter pub get` fail).
    """
    replaced: list[str] = []

    def swap(match: re.Match[str]) -> str:
        if match.group(2) != tag:
            replaced.append(match.group(2))
        return match.group(1) + tag + (match.group(3) if match.lastindex and match.lastindex >= 3 else "")

    def swap_lock(match: re.Match[str]) -> str:
        if commit is None:
            return match.group(0)
        if match.group(3) != tag or match.group(7) != commit:
            replaced.append(match.group(3))
        quote = match.group(2)
        return (match.group(1) + quote + tag + match.group(4) + match.group(5) + match.group(6)
                + commit + match.group(8) + match.group(9))

    def swap_pubspec(match: re.Match[str]) -> str:
        if match.group("ref") != tag:
            replaced.append(match.group("ref"))
        return match.group("ind") + match.group("head") + tag

    for pattern in (_DEPENDENCY, _WORKFLOW_INLINE, _WORKFLOW_BLOCK, _TARBALL):
        text = pattern.sub(swap, text)
    text = _PUBSPEC.sub(swap_pubspec, text)
    text = _LOCK.sub(swap_lock, text)
    return text, replaced


def consumers(workspace: Path) -> list[Path]:
    found = []
    for repo in sorted(workspace.iterdir()):
        if repo.is_dir() and (repo.name == "HYDRA-UMC" or repo.name.startswith("HYDRA-UMC-")) and repo.name != "HYDRA-UMC-SDK":
            found.append(repo)
    return found


def scanned_files(repo: Path) -> list[Path]:
    """Every file of a consumer that may name the SDK: manifests, locks and every workflow."""
    files = [repo / relative for relative in SCANNED]
    workflows = repo / WORKFLOWS
    if workflows.is_dir():
        files += sorted(path for path in workflows.iterdir() if path.suffix in (".yml", ".yaml"))
    return [path for path in files if path.is_file()]


def process(workspace: Path, tag: str, write: bool, commit: str | None = None) -> list[tuple[str, list[str]]]:
    changes: list[tuple[str, list[str]]] = []
    for repo in consumers(workspace):
        for path in scanned_files(repo):
            relative = path.relative_to(repo).as_posix()
            raw = path.read_bytes().decode("utf-8")
            new, replaced = repin(raw, tag, commit)
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
    changes = process(args.workspace.resolve(), tag, write=not args.check, commit=tag_commit(tag))
    for where, refs in changes:
        print(("not on " if args.check else "pinned to ") + f"{tag}: {where} (was {', '.join(refs)})")
    verdict = "FAIL" if (args.check and changes) else "PASS"
    print(f"SDK_PIN={verdict} tag={tag} references={len(changes)}")
    return 1 if (args.check and changes) else 0


if __name__ == "__main__":
    raise SystemExit(main())
