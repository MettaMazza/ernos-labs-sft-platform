@echo off
cd /d "%~dp0\.."
py -3 -m sft.mathematics.calculator_browser
if errorlevel 1 python -m sft.mathematics.calculator_browser
