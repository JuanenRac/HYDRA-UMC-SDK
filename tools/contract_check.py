#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Contract check of a whole workspace
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Walks every HYDRA-UMC repository of a workspace and reports, as JSON, what
breaks a contract of the family:

* the project manifest does not pass the SDK validator (`ProjectManifest`),
* the manifest name is not the name of the folder,
* a vendored shared tool differs from the canonical copy of this SDK,
* the manifest declares a `service` block but the port registry does not know it,
* the OpenAPI documents of this SDK are structurally broken.

Usage: python tools/contract_check.py [WORKSPACE] [--report-only] [--tables]

With `--tables` it prints, instead of the JSON report, the three tables of the
ecosystem that must never be written by hand, as Markdown: the ports of the
services (from the port registry), the version of every repository (from its
manifest) and the routes of the server (from the OpenAPI documents).

The workspace defaults to the folder that holds this SDK. The report goes to
stdout; the exit status is 1 when any problem was found (0 with
`--report-only`). Read-only: nothing is written anywhere.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

SDK_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SDK_ROOT / "clients" / "python" / "src"))

from hydra_umc_sdk.validation import ContractValidationError, validate  # noqa: E402


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def manifest_problems(repo: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        manifest = json.loads((repo / "hydra-umc.project.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return None, [f"manifest cannot be read: {error}"]
    problems: list[str] = []
    try:
        validate("ProjectManifest", manifest)
    except ContractValidationError as error:
        problems.append(f"manifest: {error}")
    if manifest.get("name") != repo.name:
        problems.append(f"manifest name {manifest.get('name')!r} is not the folder name {repo.name!r}")
    return manifest, problems


def registered_services(ports_file: Path) -> set[str]:
    """Repository names that appear in the port registry."""
    if not ports_file.is_file():
        return set()
    found: set[str] = set()
    for line in ports_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip().lstrip("- ")
        if stripped.startswith("name: HYDRA-UMC"):
            found.add(stripped[len("name: "):].strip())
    return found


def check_workspace(workspace: Path, sdk_root: Path = SDK_ROOT) -> dict[str, Any]:
    sync = _load("_contract_check_sync", sdk_root / "tools" / "sync_repo_tools.py")
    registry = registered_services(sdk_root / "contracts" / "ports.yaml")
    reports: list[dict[str, Any]] = []
    for repo in sync.repos(workspace):
        manifest, problems = manifest_problems(repo)
        problems += [f"shared tool differs: {path}" for path in sync.drift_of_repository(repo)]
        if manifest is not None and isinstance(manifest.get("service"), dict) and registry and repo.name not in registry:
            problems.append("a service that the port registry does not list")
        reports.append({"name": repo.name, "version": (manifest or {}).get("version"), "problems": problems})
    openapi = _load("_contract_check_openapi", sdk_root / "tools" / "verify_openapi.py")
    openapi_problems: list[str] = []
    for path in sorted((sdk_root / "contracts" / "openapi" / "v1").glob("*.openapi.json")):
        try:
            openapi.verify_document(path)
        except SystemExit:
            openapi_problems.append(f"{path.name}: structural check failed (see stderr)")
    failing = [r for r in reports if r["problems"]]
    return {
        "workspace": str(workspace),
        "repositories": reports,
        "openapi": openapi_problems,
        "summary": {
            "repositories": len(reports),
            "with_problems": len(failing),
            "problems": sum(len(r["problems"]) for r in reports) + len(openapi_problems),
        },
    }


HTTP_METHODS = ("get", "put", "post", "delete", "patch", "head", "options")


def _cell(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def _table(header: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(" --- " for _ in header) + "|"]
    lines += ["| " + " | ".join(_cell(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def ports_table(ports_file: Path) -> str:
    """The port registry as a Markdown table, ordered by port."""
    services: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in ports_file.read_text(encoding="utf-8").splitlines() if ports_file.is_file() else []:
        stripped = line.strip()
        if stripped.startswith("- name:"):
            current = {"name": stripped[len("- name:"):].strip()}
            services.append(current)
        elif current is not None and ":" in stripped and not stripped.startswith("#"):
            key, _, value = stripped.partition(":")
            current[key.strip()] = "" if value.strip() == "null" else value.strip()
    services.sort(key=lambda item: (int(item.get("port", "0") or 0), item["name"]))
    return _table(["Port", "Repository", "Health path", "systemd unit"], [
        [item.get("port", ""), item["name"], item.get("health_path", ""), item.get("systemd_unit", "")] for item in services
    ])


def versions_table(workspace: Path, sdk_root: Path = SDK_ROOT) -> str:
    """The version of every repository of the workspace, from its manifest, ordered by name."""
    sync = _load("_contract_check_sync", sdk_root / "tools" / "sync_repo_tools.py")
    rows: list[list[object]] = []
    for repo in sync.repos(workspace):
        manifest, _problems = manifest_problems(repo)
        rows.append([repo.name, (manifest or {}).get("version", "?"), (manifest or {}).get("maturity", "?")])
    rows.sort(key=lambda row: str(row[0]).casefold())
    return _table(["Repository", "Version", "Maturity"], rows)


def routes_table(openapi_dir: Path) -> str:
    """Every path and method of every OpenAPI document, with its operation id and tag."""
    rows: list[list[object]] = []
    for path in sorted(openapi_dir.glob("*.openapi.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        for route, item in document.get("paths", {}).items():
            for method in HTTP_METHODS:
                operation = item.get(method)
                if isinstance(operation, dict):
                    rows.append([path.name, method.upper(), route, operation.get("operationId", ""), ", ".join(operation.get("tags", []))])
    rows.sort(key=lambda row: (row[0], row[2], HTTP_METHODS.index(str(row[1]).lower())))
    return _table(["Document", "Method", "Route", "Operation", "Tag"], rows)


def tables(workspace: Path, sdk_root: Path = SDK_ROOT) -> str:
    return "\n\n".join([
        "### Ports", ports_table(sdk_root / "contracts" / "ports.yaml"),
        "### Versions", versions_table(workspace, sdk_root),
        "### Routes", routes_table(sdk_root / "contracts" / "openapi" / "v1"),
    ]) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the contracts of every HYDRA-UMC repository of a workspace.")
    parser.add_argument("workspace", nargs="?", default=str(SDK_ROOT.parent))
    parser.add_argument("--report-only", action="store_true", help="exit 0 even when problems were found")
    parser.add_argument("--tables", action="store_true", help="print the ports, versions and routes tables as Markdown instead of the report")
    args = parser.parse_args(argv)
    if args.tables:
        sys.stdout.write(tables(Path(args.workspace)))
        return 0
    report = check_workspace(Path(args.workspace))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if args.report_only or report["summary"]["problems"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
