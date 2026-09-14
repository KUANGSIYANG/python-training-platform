@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
    py -3 -X utf8 launch.py
) else (
    python -X utf8 launch.py
)
if errorlevel 1 pause
