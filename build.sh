#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo " CyanBukkit-MCP Build Script"
echo "=========================================="

if ! command -v conda >/dev/null 2>&1; then
    echo "ERROR: conda not found in PATH."
    exit 1
fi

if ! conda env list | grep -q '^mcpmaker '; then
    echo "ERROR: conda env 'mcpmaker' not found."
    echo "Create it first: conda create -n mcpmaker python=3.11"
    exit 1
fi

echo "Building with conda env 'mcpmaker'..."
conda run -n mcpmaker python build.py "$@"

echo ""
echo "Build complete: dist/cyanbukkit-mcp.exe"
