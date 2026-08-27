#!/usr/bin/env bash
# =============================================================================
# HYDRA-UMC-SDK - Validate the default HealthReport fixture
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
set -euo pipefail
echo " ==============================================================="
echo "  HYDRA-UMC-SDK - run.sh"
echo "  Validates the default HealthReport fixture."
echo "  Copyright (C) 2026 JuanenRac (Electro Hobby 3D)"
echo "  <electrohobby3d@gmail.com> | GPL-3.0-or-later - see LICENSE"
echo " ==============================================================="
cd "$(dirname "$0")"
trap '[ -t 0 ] && read -r -p "Press Enter to close..." _' EXIT
export PYTHONPATH="$PWD/clients/python/src"
python3 -m hydra_umc_sdk.validation HealthReport conformance/fixtures/v1/health-report.valid.json
