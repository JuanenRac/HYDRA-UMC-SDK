@echo off
REM =============================================================================
REM HYDRA-UMC-SDK - Validate the default HealthReport fixture
REM Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
REM GPL-3.0-or-later - see LICENSE
REM =============================================================================
setlocal
echo ===============================================================
echo  HYDRA-UMC-SDK - run.bat
echo  Validates the default HealthReport fixture.
echo  Copyright (C) 2026 JuanenRac (Electro Hobby 3D)
echo  ^<electrohobby3d@gmail.com^> ^| GPL-3.0-or-later - see LICENSE
echo ===============================================================
cd /d "%~dp0"
set "PYTHONPATH=%CD%\clients\python\src"
python -m hydra_umc_sdk.validation HealthReport conformance\fixtures\v1\health-report.valid.json
pause
