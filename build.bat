@echo off
REM =============================================================================
REM HYDRA-UMC-SDK - Validate v1 contracts and run SDK tests
REM Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
REM GPL-3.0-or-later - see LICENSE
REM =============================================================================
setlocal
echo ===============================================================
echo  HYDRA-UMC-SDK - build.bat
echo  Validates v1 contracts and runs SDK tests.
echo  Copyright (C) 2026 JuanenRac (Electro Hobby 3D)
echo  ^<electrohobby3d@gmail.com^> ^| GPL-3.0-or-later - see LICENSE
echo ===============================================================
cd /d "%~dp0"
set "PYTHONPATH=%CD%\clients\python\src"
echo === HYDRA-UMC-SDK build / test ===
python bump_version.py
if errorlevel 1 ( echo NATIVE VERSION BUMP FAILED. & pause & exit /b 1 )
python "%~dp0bump_manifest_version.py" --sync
if errorlevel 1 ( echo VERSION SYNCHRONIZATION FAILED. & pause & exit /b 1 )
if errorlevel 1 ( echo VERSION BUMP FAILED. & pause & exit /b 1 )
python -m unittest discover -s clients\python\tests -v
if errorlevel 1 ( echo BUILD FAILED. & pause & exit /b 1 )
echo Build OK: SDK contract tests passed.
pause
