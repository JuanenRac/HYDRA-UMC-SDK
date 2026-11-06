#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - hydra-contract-lint: every contract check of the ecosystem in one command
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""One command over the whole tree of repositories.

    python tools/hydra_contract_lint.py [WORKSPACE]            run the checks, print one line each
    python tools/hydra_contract_lint.py [WORKSPACE] --tables   print the generated tables (ports, versions, routes, topics)
    python tools/hydra_contract_lint.py --write-tables FILE    write those tables to FILE (the page the documentation links)

The checks are the ones that already exist, called in one place so that a person
(or a repository's CI) does not have to know which they are:

* `contract_check`: manifests, shared tools, the port registry, the OpenAPI
  documents and the topic registry of the 56 repositories of the workspace;
* `contract_source --check`: the generated OpenAPI documents, the vendored
  schemas and the server and the clients against the sources;
* `generate_types --check`: the TypeScript, Kotlin and Dart types.
* `generate_routes --check`: the route tables for JSON, TypeScript, Kotlin and Dart.

Exit status 1 when any check fails; read-only except for `--write-tables`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import contract_check  # noqa: E402


def run_tool(script: str, *arguments: str) -> tuple[bool, str]:
    result = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / script), *arguments], cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                            capture_output=True, check=False, env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "clients" / "python" / "src")})
    lines = (result.stdout + result.stderr).strip().splitlines()
    return result.returncode == 0, (lines[-1] if lines else "")


def lint(workspace: Path) -> list[tuple[str, bool, str]]:
    report = contract_check.check_workspace(workspace)
    summary = report["summary"]
    outcomes = [("contract_check", summary["problems"] == 0, f"{summary['repositories']} repositories, {summary['problems']} problems")]
    for label, script, arguments in (("contract_source", "contract_source.py", ("--check",)), ("generate_types", "generate_types.py", ("--check",)), ("generate_routes", "generate_routes.py", ("--check",))):
        ok, last = run_tool(script, *arguments)
        outcomes.append((label, ok, last))
    return outcomes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Every contract check of the ecosystem in one command.")
    parser.add_argument("workspace", nargs="?", default=str(ROOT.parent))
    parser.add_argument("--tables", action="store_true", help="print the generated tables instead of running the checks")
    parser.add_argument("--write-tables", metavar="FILE", help="write the generated tables to FILE")
    args = parser.parse_args(argv)
    workspace = Path(args.workspace)
    if args.tables or args.write_tables:
        text = contract_check.tables(workspace)
        if args.write_tables:
            Path(args.write_tables).write_text(text, encoding="utf-8", newline="\n")
            print(f"wrote {args.write_tables}")
        else:
            sys.stdout.write(text)
        return 0
    outcomes = lint(workspace)
    for label, ok, detail in outcomes:
        print(f"{label}={'PASS' if ok else 'FAIL'} {detail}")
    failed = [label for label, ok, _ in outcomes if not ok]
    print("CONTRACT_LINT=" + ("PASS" if not failed else "FAIL " + ", ".join(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
