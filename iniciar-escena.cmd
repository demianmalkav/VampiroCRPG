@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto fallback
py -3.12 -m proof.scene --open
if not errorlevel 1 goto end
:fallback
python -m proof.scene --open
:end
pause
