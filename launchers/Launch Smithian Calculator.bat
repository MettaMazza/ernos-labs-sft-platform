@echo off
cd /d "%~dp0\.."
py -3 -m sft.mathematics.calculator_complete --gui
if errorlevel 1 python -m sft.mathematics.calculator_complete --gui
