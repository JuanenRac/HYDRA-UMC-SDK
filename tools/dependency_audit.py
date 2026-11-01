#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/dependency_audit.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Dependency inventory, bill of materials and known-vulnerability report for the repositories of a workspace.

It reads what each repository already commits, runs nothing of it and installs nothing:

* `package-lock.json` (npm), `Cargo.lock` (crates), `go.mod` (Go modules), `pubspec.lock` (Dart packages): every locked package with its version;
* `pyproject.toml` and `requirements*.txt` (Python): a pinned `==` version counts as that version, a range counts as its lower bound (the oldest version the project
  allows), and a requirement with no number is listed without one and is not checked.

Each repository gets a CycloneDX 1.5 bill of materials (`--sbom-dir`), and the packages are checked against the OSV database (`--check`, needs the network; a
request that fails is reported, never counted as clean). The report says, for every advisory, the repository, the package, the version that is used and the version
that fixes it, so the upgrade that is safe to make can be told from the one that is a major change.

    python tools/dependency_audit.py                       # inventory only (offline)
    python tools/dependency_audit.py --check               # also ask OSV
    python tools/dependency_audit.py --sbom-dir DIR --json report.json --prefix ARMOR- --prefix URTC
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from pathlib import Path
from urllib.parse import quote

OSV_BATCH = "https://api.osv.dev/v1/querybatch"
OSV_VULN = "https://api.osv.dev/v1/vulns/"
BATCH_SIZE = 500
SKIPPED_DIRS = {".git", "node_modules", "target", "dist", "build", ".venv", "venv", "__pycache__", ".dart_tool", "vendor", ".mypy_cache", ".ruff_cache"}
FAMILY_PREFIXES = ("ARMOR", "URTC", "HYDRA-UMC")
# the fourth family has its own owner and its own tooling
EXCLUDED_PREFIXES = ("EH3D", "ELECTRO-HOBBY-3D")

_REQUIREMENT = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9_.\-]*)\s*(?:\[[^\]]*\])?\s*((?:===|==|~=|>=|<=|!=|>|<)\s*[0-9][^,;\s]*)?")


class Dependency:
    __slots__ = ("ecosystem", "name", "version", "floor", "source")

    def __init__(self, ecosystem: str, name: str, version: str, source: str, floor: bool = False) -> None:
        self.ecosystem, self.name, self.version, self.source, self.floor = ecosystem, name, version, source, floor

    def key(self) -> tuple[str, str, str]:
        return (self.ecosystem, self.name, self.version)

    def purl(self) -> str:
        kind = {"npm": "npm", "crates.io": "cargo", "Go": "golang", "PyPI": "pypi", "Pub": "pub"}[self.ecosystem]
        return f"pkg:{kind}/{quote(self.name, safe='/')}" + (f"@{self.version}" if self.version else "")


def _walk(root: Path, names: set[str], patterns: tuple[str, ...] = ()) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if any(part in SKIPPED_DIRS for part in path.relative_to(root).parts[:-1]):
            continue
        if path.is_file() and (path.name in names or any(path.match(pattern) for pattern in patterns)):
            yield path


def parse_package_lock(path: Path) -> list[Dependency]:
    data = json.loads(path.read_text(encoding="utf-8"))
    found: list[Dependency] = []
    for key, entry in (data.get("packages") or {}).items():
        if not key or not isinstance(entry, dict) or "version" not in entry or entry.get("link"):
            continue
        name = entry.get("name") or key.rsplit("node_modules/", 1)[-1]
        found.append(Dependency("npm", name, str(entry["version"]), path.name))
    return found


def parse_cargo_lock(path: Path) -> list[Dependency]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return [Dependency("crates.io", p["name"], p["version"], path.name) for p in data.get("package", []) if p.get("source", "").startswith("registry")]


def parse_go_mod(path: Path) -> list[Dependency]:
    found: list[Dependency] = []
    in_block = False
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("//", 1)[0].strip()
        if line.startswith("require ("):
            in_block = True
            continue
        if in_block and line == ")":
            in_block = False
            continue
        spec = line[len("require "):].strip() if line.startswith("require ") else (line if in_block else "")
        parts = spec.split()
        if len(parts) >= 2 and parts[1].startswith("v"):
            found.append(Dependency("Go", parts[0], parts[1].removeprefix("v"), path.name))
    return found


def parse_pubspec_lock(path: Path) -> list[Dependency]:
    found: list[Dependency] = []
    name = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^  ([A-Za-z0-9_]+):\s*$", line)
        if match:
            name = match.group(1)
            continue
        match = re.match(r'^    version: "?([^"\s]+)"?\s*$', line)
        if match and name:
            found.append(Dependency("Pub", name, match.group(1), path.name))
            name = ""
    return found


def _requirement(spec: str, source: str) -> Dependency | None:
    spec = spec.split(";", 1)[0].strip()
    if not spec or spec.startswith(("#", "-")) or " @ " in spec or "://" in spec:
        return None
    match = _REQUIREMENT.match(spec)
    if not match:
        return None
    name, constraint = match.group(1), (match.group(2) or "").replace(" ", "")
    if constraint.startswith(("==", "===")):
        return Dependency("PyPI", name, constraint.lstrip("="), source)
    if constraint.startswith((">=", "~=", ">")):
        return Dependency("PyPI", name, constraint.lstrip(">=~"), source, floor=True)
    return Dependency("PyPI", name, "", source)


def parse_pyproject(path: Path) -> list[Dependency]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    specs: list[str] = list(data.get("project", {}).get("dependencies", []))
    for group in data.get("project", {}).get("optional-dependencies", {}).values():
        specs += list(group)
    for group in (data.get("dependency-groups") or {}).values():
        specs += [item for item in group if isinstance(item, str)]
    return [dep for dep in (_requirement(spec, path.name) for spec in specs) if dep]


def parse_requirements(path: Path) -> list[Dependency]:
    return [dep for dep in (_requirement(line, path.name) for line in path.read_text(encoding="utf-8").splitlines()) if dep]


PARSERS: tuple[tuple[str, Callable[[Path], list[Dependency]]], ...] = (
    ("package-lock.json", parse_package_lock),
    ("Cargo.lock", parse_cargo_lock),
    ("go.mod", parse_go_mod),
    ("pubspec.lock", parse_pubspec_lock),
    ("pyproject.toml", parse_pyproject),
)


def inventory(repo: Path) -> list[Dependency]:
    """Every dependency a repository commits, once per ecosystem, name and version."""
    found: dict[tuple[str, str, str], Dependency] = {}
    wanted = {name for name, _ in PARSERS}
    for path in _walk(repo, wanted, ("requirements*.txt",)):
        parser = dict(PARSERS).get(path.name, parse_requirements)
        try:
            for dep in parser(path):
                found.setdefault(dep.key(), dep)
        except (OSError, ValueError, KeyError) as error:
            print(f"{repo.name}/{path.relative_to(repo)}: cannot be read ({error})", file=sys.stderr)
    return sorted(found.values(), key=lambda d: d.key())


def bill_of_materials(repo: str, dependencies: list[Dependency]) -> dict:
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {"component": {"type": "application", "name": repo}},
        "components": [
            {"type": "library", "name": d.name, "version": d.version, "purl": d.purl(), **({"properties": [{"name": "version-is", "value": "lower-bound"}]} if d.floor else {})}
            for d in dependencies
        ],
    }


def _post(url: str, body: dict) -> dict:
    request = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 - fixed https URL
        return json.loads(response.read())


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310 - fixed https URL
        return json.loads(response.read())


def query_osv(
    keys: list[tuple[str, str, str]],
    post: Callable[[str, dict], dict] = _post,
    get: Callable[[str], dict] = _get,
) -> tuple[dict[tuple[str, str, str], list[dict]], list[str]]:
    """(advisories by (ecosystem, name, version), problems). A package whose request failed is a problem, never a clean result."""
    checkable = [k for k in keys if k[2]]
    advisories: dict[tuple[str, str, str], list[dict]] = {}
    problems: list[str] = []
    cache: dict[str, dict] = {}
    for start in range(0, len(checkable), BATCH_SIZE):
        chunk = checkable[start:start + BATCH_SIZE]
        queries = [{"package": {"name": name, "ecosystem": eco}, "version": version} for eco, name, version in chunk]
        try:
            results = post(OSV_BATCH, {"queries": queries}).get("results", [])
        except (urllib.error.URLError, OSError, ValueError) as error:
            problems.append(f"OSV batch {start}-{start + len(chunk)}: {error}")
            continue
        for key, result in zip(chunk, results):
            for vuln in result.get("vulns", []):
                advisories.setdefault(key, []).append({"id": vuln["id"]})
    for key, items in advisories.items():
        for item in items:
            if item["id"] not in cache:
                try:
                    cache[item["id"]] = get(OSV_VULN + item["id"])
                except (urllib.error.URLError, OSError, ValueError) as error:
                    problems.append(f"OSV {item['id']}: {error}")
                    cache[item["id"]] = {}
            detail = cache[item["id"]]
            item["summary"] = (detail.get("summary") or "")[:160]
            item["fixed"] = sorted(_fixed_versions(detail, key))
            item["severity"] = _severity(detail)
    return advisories, problems


def _fixed_versions(detail: dict, key: tuple[str, str, str]) -> set[str]:
    fixed: set[str] = set()
    for affected in detail.get("affected", []):
        package = affected.get("package", {})
        if package.get("name") != key[1]:
            continue
        for rng in affected.get("ranges", []):
            for event in rng.get("events", []):
                if "fixed" in event:
                    fixed.add(event["fixed"])
    return fixed


def _severity(detail: dict) -> str:
    return str((detail.get("database_specific") or {}).get("severity") or "").upper() or "UNKNOWN"


def family_repositories(workspace: Path, prefixes: tuple[str, ...]) -> list[Path]:
    return sorted(
        p for p in workspace.iterdir()
        if p.is_dir() and p.name.startswith(prefixes) and not p.name.startswith(EXCLUDED_PREFIXES) and (p / ".git").exists()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--prefix", action="append", help="only repositories whose name starts with this (default: the three families)")
    parser.add_argument("--check", action="store_true", help="ask the OSV database about every package that has a version")
    parser.add_argument("--sbom-dir", type=Path, help="write one CycloneDX bill of materials per repository here")
    parser.add_argument("--json", type=Path, help="write the full report here")
    args = parser.parse_args(argv)

    prefixes = tuple(args.prefix) if args.prefix else FAMILY_PREFIXES
    per_repo = {repo.name: inventory(repo) for repo in family_repositories(args.workspace.resolve(), prefixes)}
    if args.sbom_dir:
        args.sbom_dir.mkdir(parents=True, exist_ok=True)
        for name, deps in per_repo.items():
            if deps:
                (args.sbom_dir / f"{name}.cdx.json").write_text(json.dumps(bill_of_materials(name, deps), indent=1) + "\n", encoding="utf-8")
    unique = sorted({d.key() for deps in per_repo.values() for d in deps})
    print(f"repositories={len(per_repo)} with_dependencies={sum(1 for d in per_repo.values() if d)} unique_packages={len(unique)}")

    advisories: dict[tuple[str, str, str], list[dict]] = {}
    problems: list[str] = []
    if args.check:
        advisories, problems = query_osv(unique)
        for key in sorted(advisories):
            users = sorted(name for name, deps in per_repo.items() if any(d.key() == key for d in deps))
            for item in advisories[key]:
                fixed = ",".join(item["fixed"]) or "no fix listed"
                print(f"{item['severity']:9} {key[0]}:{key[1]}@{key[2]} {item['id']} fixed in {fixed} used by {', '.join(users[:6])}{' +%d' % (len(users) - 6) if len(users) > 6 else ''}")
        for problem in problems:
            print("PROBLEM " + problem)
        print(f"DEPENDENCY_AUDIT={'PASS' if not advisories and not problems else 'FINDINGS'} advisories={sum(len(v) for v in advisories.values())} packages_affected={len(advisories)} problems={len(problems)}")
    if args.json:
        args.json.write_text(
            json.dumps(
                {
                    "repositories": {n: [{"ecosystem": d.ecosystem, "name": d.name, "version": d.version, "lowerBound": d.floor, "source": d.source} for d in deps] for n, deps in per_repo.items()},
                    "advisories": [{"ecosystem": k[0], "name": k[1], "version": k[2], **item} for k, items in sorted(advisories.items()) for item in items],
                    "problems": problems,
                },
                indent=1,
            )
            + "\n",
            encoding="utf-8",
        )
    return 1 if args.check and problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
