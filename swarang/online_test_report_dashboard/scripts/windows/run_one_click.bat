@echo off
REM Wrapper to run the PowerShell one-click setup (useful on Windows when double-clicking)
powershell -ExecutionPolicy Bypass -File "%~dp0one_click_setup.ps1"
