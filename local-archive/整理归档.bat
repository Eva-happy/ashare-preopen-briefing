@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0tools\run.bat" organize --root "%~dp0."
if errorlevel 1 pause
