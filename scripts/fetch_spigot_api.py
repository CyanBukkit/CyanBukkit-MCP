#!/usr/bin/env python3
"""
Fetch Spigot API source files from GitHub and save as raw knowledge.
Uses GitHub API to list all Java files, then downloads them.
"""

import json
import os
import urllib.request
import urllib.parse
from pathlib import Path

RAW_BASE = "https://raw.githubusercontent.com/SpigotMC/Spigot-API/master"
API_BASE = "https://api.github.com/repos/SpigotMC/Spigot-API/contents"
OUTPUT_DIR = Path(__file__).parent.parent / "knowledge" / "raw" / "spigot_api_src"

def fetch_json(url: str) -> list | dict:
    req = urllib.request.Request(url, headers={"User-Agent": "CyanBukkit-MCP"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def download_file(download_url: str, rel_path: str):
    out_path = OUTPUT_DIR / rel_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(download_url, headers={"User-Agent": "CyanBukkit-MCP"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        out_path.write_bytes(resp.read())
    print(f"  OK {rel_path}")

def walk_and_download(github_path: str):
    """Recursively walk GitHub API tree and download .java files."""
    url = API_BASE + github_path
    try:
        items = fetch_json(url)
    except Exception as e:
        print(f"  ✗ Failed to list {github_path}: {e}")
        return

    for item in items:
        if item["type"] == "dir":
            walk_and_download(item["path"].replace("src/main/java/", "/"))
        elif item["type"] == "file" and item["name"].endswith(".java"):
            rel = item["path"].replace("src/main/java/", "").replace("/", os.sep)
            download_file(item["download_url"], rel)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Fetching Spigot API source files from GitHub...")
    print(f"Output: {OUTPUT_DIR}")
    print()

    # Start from src/main/java/org/bukkit
    walk_and_download("/src/main/java/org/bukkit")
    print()
    print("Done!")

if __name__ == "__main__":
    main()
