@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在同步到 GitHub（api.github.com 直传，绕开 github.com 被污染）
python tools\publish.py %*
echo.
pause
