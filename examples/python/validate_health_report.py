# =============================================================================
# HYDRA-UMC-SDK - HealthReport validation example
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

"""Validate a HealthReport fixture with the SDK reference client."""

import json
from pathlib import Path

from hydra_umc_sdk.validation import validate


fixture = Path(__file__).parents[2] / "conformance" / "fixtures" / "v1" / "health-report.valid.json"
validate("HealthReport", json.loads(fixture.read_text(encoding="utf-8")))
print("HealthReport fixture is valid")
