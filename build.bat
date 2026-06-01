@echo off
setlocal

echo ==========================================
echo  CyanBukkit-MCP Build Script
echo ==========================================

where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: conda not found in PATH.
    echo Please install Miniconda or add conda to PATH.
    exit /b 1
)

conda env list | findstr /R /C:"^mcpmaker " >nul
if %errorlevel% neq 0 (
    echo ERROR: conda env 'mcpmaker' not found.
    echo Create it first: conda create -n mcpmaker python=3.11
    exit /b 1
)

echo Building with conda env 'mcpmaker'...
conda run -n mcpmaker python build.py %*
if %errorlevel% neq 0 (
    echo Build failed.
    exit /b 1
)

echo.
echo Build complete: dist\cyanbukkit-mcp.exe
