import argparse
import json
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRADLE_ROOT = Path(r"D:\Program Files\gradle")
DEFAULT_CLASSES_DIR = PROJECT_ROOT / "knowledge" / "processed" / "nms_classes"
DEFAULT_INDEX_DIR = PROJECT_ROOT / "knowledge" / "processed" / "nms_index"
NMS_PREFIX = "net/minecraft/server/"
ARTIFACT_RE = re.compile(r"(spigot|minecraft-server)-([0-9][^-]+)-R0\.1-SNAPSHOT", re.I)


def discover_jars(roots: Iterable[Path]) -> List[Path]:
    jars = []
    for root in roots:
        if not root.exists():
            continue
        for jar in root.rglob("*.jar"):
            name = jar.name.lower()
            if ("spigot" in name or "minecraft-server" in name) and "sources" not in name:
                jars.append(jar)
    return sorted(set(jars))


def parse_version(jar: Path) -> str:
    match = ARTIFACT_RE.search(jar.name)
    if match:
        return match.group(2)
    parts = jar.parts
    for part in reversed(parts):
        if re.match(r"^[0-9]+\.[0-9]+", part):
            return part
    return "unknown"


def class_name_from_entry(entry: str) -> str:
    return entry[:-6].replace("/", ".")


def run_javap(jar: Path, class_name: str) -> List[Dict[str, str]]:
    try:
        proc = subprocess.run(
            ["javap", "-classpath", str(jar), "-public", class_name],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception:
        return []
    methods = []
    for line in proc.stdout.splitlines():
        stripped = line.strip().rstrip(";")
        if "(" in stripped and ")" in stripped and not stripped.startswith("Compiled from"):
            methods.append({"signature": stripped})
    return methods


def extract_jar(jar: Path, limit: Optional[int], include_methods: bool) -> Dict[str, Any]:
    version = parse_version(jar)
    classes = []
    with zipfile.ZipFile(jar) as zf:
        entries = [name for name in zf.namelist() if name.startswith(NMS_PREFIX) and name.endswith(".class") and "$" not in name]
    if limit is not None:
        entries = entries[:limit]
    for entry in entries:
        class_name = class_name_from_entry(entry)
        short_name = class_name.rsplit(".", 1)[-1]
        package = class_name.rsplit(".", 1)[0]
        item = {
            "class_name": class_name,
            "short_name": short_name,
            "package": package,
            "minecraft_version": version,
            "methods": run_javap(jar, class_name) if include_methods else [],
            "source_jar": str(jar),
        }
        classes.append(item)
    return {"minecraft_version": version, "source_jar": str(jar), "class_count": len(classes), "classes": classes}


def save_result(result: Dict[str, Any]) -> None:
    version = result["minecraft_version"]
    version_dir = DEFAULT_CLASSES_DIR / version
    version_dir.mkdir(parents=True, exist_ok=True)
    DEFAULT_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    for item in result["classes"]:
        target = version_dir / f"{item['class_name'].replace('.', '_')}.json"
        with open(target, "w", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
    with open(DEFAULT_INDEX_DIR / f"{version}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract versioned NMS class knowledge from Spigot/Minecraft server jars.")
    parser.add_argument("--gradle-root", type=Path, default=DEFAULT_GRADLE_ROOT)
    parser.add_argument("--root", action="append", type=Path, help="Additional root to scan for jars.")
    parser.add_argument("--version", help="Only process jars whose parsed version matches this value.")
    parser.add_argument("--limit", type=int, help="Limit classes per jar.")
    parser.add_argument("--include-methods", action="store_true", help="Run javap to extract public method signatures.")
    parser.add_argument("--dry-run", action="store_true", help="List matching jars without writing output.")
    args = parser.parse_args()

    roots = [args.gradle_root]
    if args.root:
        roots.extend(args.root)
    jars = discover_jars(roots)
    if args.version:
        jars = [jar for jar in jars if parse_version(jar) == args.version]

    print(f"Found {len(jars)} candidate jar(s)")
    for jar in jars[:50]:
        print(f"- {parse_version(jar)} {jar}")
    if args.dry_run:
        return

    for jar in jars:
        result = extract_jar(jar=jar, limit=args.limit, include_methods=args.include_methods)
        if result["class_count"]:
            save_result(result)
            print(f"Saved {result['class_count']} NMS class(es) for {result['minecraft_version']}")


if __name__ == "__main__":
    main()
