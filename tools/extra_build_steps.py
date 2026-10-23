#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/extra_build_steps.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The steps of this repository beyond the shared build test: the contract checks and the native clients."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fail(message: str) -> None:
    print(f"BUILD_TEST=FAIL {message}", file=sys.stderr)
    raise SystemExit(1)


def run(*command: str, cwd: Path = ROOT, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(command))
    try:
        subprocess.run(command, cwd=cwd, env=env, check=True)
    except FileNotFoundError:
        fail(f"required command not found: {command[0]}")
    except subprocess.CalledProcessError as exc:
        fail(f"command failed with exit code {exc.returncode}: {' '.join(command)}")


def run_contract_checks() -> None:
    environment = dict(os.environ)
    client_source = str(ROOT / "clients" / "python" / "src")
    existing_python_path = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = client_source if not existing_python_path else os.pathsep.join((client_source, existing_python_path))
    run(sys.executable, "-m", "unittest", "discover", "-s", "clients/python/tests", "-v", env=environment)
    run(sys.executable, "tools/verify_contract_matrix.py", env=environment)
    run(sys.executable, "tools/verify_openapi.py", env=environment)


def run_native_clients() -> None:
    """Runs the Go, TypeScript and Rust client tests when their toolchain exists."""
    clients = ROOT / "clients"
    npm = "npm.cmd" if os.name == "nt" else "npm"
    plans = (
        ("go", clients / "go" / "go.mod", ("go", "test", "./..."), clients / "go"),
        ("npm", clients / "typescript" / "package.json", None, clients / "typescript"),
        ("cargo", clients / "rust" / "Cargo.toml", ("cargo", "test", "--all-targets"), clients / "rust"),
    )
    for tool, marker, command, directory in plans:
        label = {"go": "GO_CLIENT", "npm": "TYPESCRIPT_CLIENT", "cargo": "RUST_CLIENT"}[tool]
        if not marker.is_file():
            continue
        if shutil.which(tool if tool != "npm" else npm) is None:
            print(f"{label}=SKIPPED {tool} is not installed on this host")
            continue
        if tool == "npm":
            if not (directory / "node_modules").is_dir():
                run(npm, "ci", "--ignore-scripts", cwd=directory)
            run(npm, "test", "--if-present", cwd=directory)
        else:
            run(*command, cwd=directory)
        print(f"{label}=PASS")


def main() -> int:
    if (ROOT / "clients" / "python" / "tests").is_dir():
        run_contract_checks()
    run_native_clients()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
