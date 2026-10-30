#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/ecosystem_release.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The one file that says which versions of the repositories go together: `ecosystem-release.json`.

For a release of the family it names the version and the commit of every repository. This tool writes it, from the
manifests and the Git heads of the repositories checked out side by side; it is published in the documentation
repository (`HYDRA-UMC-DOCS/data/ecosystem-release.json`), and the shared validator (`tools/ci_validate.py`) checks the
entry of the repository it runs in when that checkout is at hand.

    python tools/ecosystem_release.py --write    # (re)write the file in the documentation repository
    python tools/ecosystem_release.py --check    # exit 1 when the file is malformed or disagrees with a repository
    python tools/ecosystem_release.py --print    # show what --write would write

Run `--write` for each release of the family, then commit the file in the documentation repository. Options:
`--workspace DIR` (the folder holding the repositories; default: the parent of the SDK) and `--docs DIR` (the
documentation repository; default: `HYDRA-UMC-DOCS` in the workspace).

File shape: `{"schema_version": "1.0", "ecosystem": "HYDRA-UMC", "repositories": [{"name", "version", "commit"}, ...]}`
sorted by name. A repository is "in step" when its manifest version is the listed one or a later one and the listed
commit is in its history.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parents[1]
FILE_NAME = "ecosystem-release.json"
SCHEMA_VERSION = "1.0"
ECOSYSTEM = "HYDRA-UMC"
_VERSION = re.compile(r"^\d+(?:\.\d+){2,3}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")


def is_family_repo(path: Path) -> bool:
    name = path.name
    return path.is_dir() and (name == "HYDRA-UMC" or name.startswith("HYDRA-UMC-")) and (path / "hydra-umc.project.json").is_file()


def version_key(value: str) -> tuple[int, ...]:
    parts = tuple(int(part) for part in value.split("."))
    return parts + (0,) * (4 - len(parts))


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)


def head_commit(root: Path) -> str | None:
    try:
        result = _git(root, "rev-parse", "HEAD")
    except OSError:
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and _COMMIT.match(value) else None


def manifest_version(root: Path) -> str | None:
    try:
        value = json.loads((root / "hydra-umc.project.json").read_text(encoding="utf-8")).get("version")
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, str) and _VERSION.match(value) else None


def build(workspace: Path) -> dict[str, object]:
    entries: list[dict[str, str]] = []
    for repo in sorted(p for p in workspace.iterdir() if is_family_repo(p)):
        version, commit = manifest_version(repo), head_commit(repo)
        if version is None or commit is None:
            raise SystemExit(f"{repo.name}: no readable manifest version or no Git commit; fix it before writing the release file")
        entries.append({"name": repo.name, "version": version, "commit": commit})
    return {"schema_version": SCHEMA_VERSION, "ecosystem": ECOSYSTEM, "repositories": entries}


def render(data: dict[str, object]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def problems_of_file(data: object) -> list[str]:
    """What is wrong with the file by itself (shape, order, duplicates)."""
    if not isinstance(data, dict):
        return ["the release file is not an object"]
    found: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        found.append(f"schema_version must be {SCHEMA_VERSION!r}")
    if data.get("ecosystem") != ECOSYSTEM:
        found.append(f"ecosystem must be {ECOSYSTEM!r}")
    repositories = data.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        return found + ["repositories must be a non-empty list"]
    names: list[str] = []
    for position, entry in enumerate(repositories):
        if not isinstance(entry, dict) or set(entry) != {"name", "version", "commit"}:
            found.append(f"entry {position} must have exactly name, version and commit")
            continue
        name, version, commit = entry["name"], entry["version"], entry["commit"]
        if not isinstance(name, str) or not (name == "HYDRA-UMC" or name.startswith("HYDRA-UMC-")):
            found.append(f"entry {position}: name {name!r} is not a repository of the family")
            continue
        names.append(name)
        if not isinstance(version, str) or not _VERSION.match(version):
            found.append(f"{name}: version {version!r} is not MAJOR.MINOR.PATCH[.BUILD]")
        if not isinstance(commit, str) or not _COMMIT.match(commit):
            found.append(f"{name}: commit must be 40 lowercase hexadecimal characters")
    if len(set(names)) != len(names):
        found.append("a repository is listed twice")
    if names != sorted(names):
        found.append("repositories must be sorted by name")
    return found


def problems_of_entry(entry: dict[str, str], root: Path) -> list[str]:
    """What disagrees between one listed entry and the repository checked out at `root`."""
    found: list[str] = []
    current = manifest_version(root)
    if current is not None and _VERSION.match(entry["version"]) and version_key(entry["version"]) > version_key(current):
        found.append(f"{entry['name']}: the release file lists version {entry['version']}, ahead of the manifest ({current})")
    try:
        shallow = _git(root, "rev-parse", "--is-shallow-repository").stdout.strip() == "true"
        inside = _git(root, "rev-parse", "--is-inside-work-tree").stdout.strip() == "true"
        if inside and not shallow:
            known = _git(root, "cat-file", "-e", entry["commit"] + "^{commit}")
            if known.returncode != 0:
                found.append(f"{entry['name']}: the release file lists commit {entry['commit'][:12]}, which is not in the history")
    except OSError:
        pass
    return found


def check(data: object, workspace: Path) -> list[str]:
    found = problems_of_file(data)
    if found:
        return found
    for entry in data["repositories"]:  # type: ignore[index]
        repo = workspace / entry["name"]
        if repo.is_dir():
            found.extend(problems_of_entry(entry, repo))
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--print", action="store_true", dest="show")
    parser.add_argument("--workspace", type=Path, default=SDK_ROOT.parent)
    parser.add_argument("--docs", type=Path, default=None)
    args = parser.parse_args(argv)
    workspace = args.workspace.resolve()
    docs = (args.docs or workspace / "HYDRA-UMC-DOCS").resolve()
    target = docs / "data" / FILE_NAME

    if args.show:
        sys.stdout.write(render(build(workspace)))
        return 0
    if args.write:
        if not (docs / "hydra-umc.project.json").is_file():
            print(f"ECOSYSTEM_RELEASE=FAIL the documentation repository was not found at {docs}", file=sys.stderr)
            return 1
        data = build(workspace)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(data), encoding="utf-8", newline="\n")
        print(f"ECOSYSTEM_RELEASE=WRITTEN repositories={len(data['repositories'])} file={target}")  # type: ignore[arg-type]
        return 0
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ECOSYSTEM_RELEASE=FAIL cannot read {target}: {exc}", file=sys.stderr)
        return 1
    found = check(data, workspace)
    for line in found:
        print("ECOSYSTEM_RELEASE: " + line)
    verdict = "FAIL" if found else "PASS"
    print(f"ECOSYSTEM_RELEASE={verdict} problems={len(found)}")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
