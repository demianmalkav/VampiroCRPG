@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto fallback
py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
if errorlevel 1 goto missing
py -3 -m proof.walk --open
goto end
:fallback
where python >nul 2>nul
if errorlevel 1 goto missing
python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
if errorlevel 1 goto missing
python -m proof.walk --open
goto end
:missing
echo Necesitas Python 3.11 o posterior. Consulta LEEME.txt.
:end
pause
