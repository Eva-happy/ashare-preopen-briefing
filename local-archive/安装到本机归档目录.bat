@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set "DEST=D:\Eva-personal\A股开盘前早报归档"
call "%~dp0tools\run.bat" install --dest "%DEST%" --repo-root "%~dp0.."
if errorlevel 1 (
  pause
  exit /b 1
)
echo.
echo 已整理到 %DEST%
echo 早盘报告在「早盘」文件夹，收盘报告在「收盘」文件夹。
echo 双击「生成收盘报告.bat」会下载最新收盘 HTML。
explorer "%DEST%"
pause
