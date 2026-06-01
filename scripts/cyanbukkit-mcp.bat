@echo off
setlocal

set "MCPMAKER_PYTHON=C:\ProgramData\miniconda3\envs\mcpmaker\python.exe"

if not exist "%MCPMAKER_PYTHON%" (
    echo ERROR: Python not found at %MCPMAKER_PYTHON%
    echo Please ensure conda env 'mcpmaker' exists.
    exit /b 1
)

set "PYTHONPATH=%~dp0..\src;%PYTHONPATH%"
"%MCPMAKER_PYTHON%" -m cyanbukkit_mcp %*
