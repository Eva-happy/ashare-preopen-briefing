@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0tools\run.bat" fetch --kind open --root "%~dp0." --open
if errorlevel 1 pause
