@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0tools\run.bat" fetch --kind close --root "%~dp0." --open
if errorlevel 1 pause
