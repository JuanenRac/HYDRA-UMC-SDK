#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Generate immutable JSON Schema contract manifest
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "json-schema" / "v1"
entries = []
for path in sorted(ROOT.glob("*.schema.json")):
    entries.append({"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
print(json.dumps({"schema_version": "1.0", "contracts": entries}, indent=2) + "\n")
