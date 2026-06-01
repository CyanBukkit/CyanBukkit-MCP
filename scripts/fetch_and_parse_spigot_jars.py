#!/usr/bin/env python3
"""
Batch download Spigot API jars from maven.elmakers.com,
extract public API signatures using javap, and save to JSON.
"""
import json
import os
import re
import ssl
import subprocess
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any

# Config
JAVAP_PATH = r"C:\Program Files\Java\jdk-21\bin\javap.exe"
BASE_URL = "https://maven.elmakers.com/repository/org/spigotmc/spigot-api/"
OUTPUT_BASE = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\maven_jars")
API_OUTPUT = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\plugin_apis")
MAX_WORKERS = 4

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        return resp.read().decode("utf-8")


def get_versions() -> List[str]:
    html = fetch_html(BASE_URL)
    versions = re.findall(r'href="([^"/]+/)"', html)
    return sorted([v.rstrip("/") for v in versions if v != "../"])


def find_jar_url(version: str) -> tuple:
    listing_url = f"{BASE_URL}{version}/"
    html = fetch_html(listing_url)
    files = re.findall(r'href="([^"]+\.jar)"', html)
    main_jars = [
        f for f in files
        if "-shaded" not in f and "-sources" not in f and "-javadoc" not in f
    ]
    if main_jars:
        return listing_url + main_jars[0], main_jars[0]
    return None, None


def download_jar(version: str, url: str, filename: str) -> Path:
    version_dir = OUTPUT_BASE / version
    version_dir.mkdir(parents=True, exist_ok=True)
    jar_path = version_dir / filename

    if jar_path.exists() and jar_path.stat().st_size > 1000:
        return jar_path

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        data = resp.read()
        with open(jar_path, "wb") as f:
            f.write(data)
    return jar_path


def extract_classes(jar_path: Path) -> List[str]:
    with zipfile.ZipFile(jar_path, "r") as zf:
        classes = [
            name.replace("/", ".").replace(".class", "")
            for name in zf.namelist()
            if name.endswith(".class")
            and "$" not in name  # skip inner classes
            and not name.startswith("META-INF")
        ]
    return classes


def parse_class(jar_path: Path, class_name: str) -> Dict[str, Any]:
    try:
        result = subprocess.run(
            [JAVAP_PATH, "-classpath", str(jar_path), "-public", class_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return {"class": class_name, "error": result.stderr[:200]}

        lines = result.stdout.splitlines()
        header = lines[0] if lines else ""

        methods = []
        fields = []
        for line in lines[1:]:
            line = line.strip().rstrip(";")
            if not line or line == "}":
                continue
            if "(" in line and ";" not in line.split("(")[0]:
                methods.append(line)
            elif "static" in line or "final" in line or "public" in line:
                fields.append(line)

        return {
            "class": class_name,
            "source": header.replace('Compiled from "', "").replace('"', ""),
            "methods": methods,
            "fields": fields,
        }
    except Exception as e:
        return {"class": class_name, "error": str(e)}


def process_version(version: str) -> Dict[str, Any]:
    print(f"[START] {version}")
    url, filename = find_jar_url(version)
    if not url:
        return {"version": version, "error": "no jar found"}

    try:
        jar_path = download_jar(version, url, filename)
        classes = extract_classes(jar_path)
        print(f"[DOWNLOADED] {version}: {jar_path.name} ({len(classes)} classes)")

        parsed = []
        for i, cls in enumerate(classes):
            if i % 100 == 0:
                print(f"  [{version}] {i}/{len(classes)} {cls}")
            parsed.append(parse_class(jar_path, cls))

        result = {
            "version": version,
            "artifact": "org.spigotmc:spigot-api",
            "source_url": url,
            "jar_file": str(jar_path.name),
            "class_count": len(classes),
            "classes": parsed,
        }

        # Save individual version JSON
        out_file = API_OUTPUT / f"spigot_api_{version.replace('.', '_').replace('-', '_')}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"[DONE] {version}: {len(classes)} classes -> {out_file.name}")
        return result

    except Exception as e:
        print(f"[ERROR] {version}: {e}")
        return {"version": version, "error": str(e)}


def main():
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    API_OUTPUT.mkdir(parents=True, exist_ok=True)

    versions = get_versions()
    print(f"Found {len(versions)} versions")

    # Process in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_version, v): v for v in versions}
        for future in as_completed(futures):
            version = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"[FATAL] {version}: {e}")

    # Build master index
    master_index = []
    for f in sorted(API_OUTPUT.glob("spigot_api_*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            master_index.append({
                "version": data.get("version"),
                "class_count": data.get("class_count", 0),
                "file": f.name,
                "error": data.get("error"),
            })
        except:
            pass

    with open(API_OUTPUT / "spigot_api_master_index.json", "w", encoding="utf-8") as f:
        json.dump(master_index, f, ensure_ascii=False, indent=2)

    print(f"\nMaster index: {len(master_index)} versions")
    print("All done!")


if __name__ == "__main__":
    main()
