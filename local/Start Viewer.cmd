@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -c "import openskp, flatbuffers" >nul 2>&1
if errorlevel 1 (
  ".venv\Scripts\python.exe" -m pip install "openskp[fragments]==1.4.0"
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" convert.py %*
if errorlevel 1 goto failed
pause
exit /b 0
:failed
echo Could not finish. Read the error above. Requires 64-bit Python 3.10 or newer.
pause
exit /b 1

