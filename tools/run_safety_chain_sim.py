#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/run_safety_chain_sim.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Run the safety-chain simulation of tests/integration: zones -> planner gate -> global stop -> operator dead-man -> watchdog.

    python tools/run_safety_chain_sim.py              # run what this machine can run; the rest is reported as skipped
    python tools/run_safety_chain_sim.py --require    # a skipped scenario is a failure
    python tools/run_safety_chain_sim.py -k fencing   # only the scenarios whose name matches

The other repositories are read from the folder next to this one (or HYDRA_CHAIN_SIM_WORKSPACE); nothing is installed in them and
nothing is written in them. The services listen on loopback only, on ports that the operating system gives at that moment. The needs:
Python with pytest; node for the dead-man of the operator (HYDRA-UMC-SERVER with its node_modules); go for the watchdog (a small
`go build` into a temporary folder, or HYDRA_UMC_NODE_HEALING_BIN). A pass means "passed in simulation": nothing here ran on hardware.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests" / "integration"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--require", action="store_true", help="a skipped scenario is a failure")
    parser.add_argument("-k", dest="keyword", default="", help="only the scenarios whose name matches")
    args = parser.parse_args()
    command = [sys.executable, "-m", "pytest", str(TESTS), "-q", "-rs", "-p", "no:cacheprovider"]
    if args.keyword:
        command += ["-k", args.keyword]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    summary = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    skipped = int(m.group(1)) if (m := re.search(r"(\d+) skipped", summary)) else 0
    if result.returncode != 0:
        print("CHAIN_SIM=FAIL")
        return 1
    if args.require and skipped:
        print(f"CHAIN_SIM=FAIL {skipped} scenario(s) skipped and --require was given")
        return 1
    print(f"CHAIN_SIM=PASS passed in simulation ({skipped} skipped)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
