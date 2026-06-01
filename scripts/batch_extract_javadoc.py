"""
Batch extract javadoc from paper-api jars in local Maven repository.
Extracts .class files to temp dir then runs javap to get method signatures.
"""

import json
import subprocess
import os
import re
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

JAVAP = r"C:\Program Files\Java\jdk-11\bin\javap.exe"
M2_REPO = Path(os.path.expanduser("C:/Users/SmallXY/.m2/repository"))

PAPER_API_JARS = [
    M2_REPO / "io/papermc/paper/paper-api/1.21.9-R0.1-SNAPSHOT/paper-api-1.21.9-R0.1-SNAPSHOT.jar",
    M2_REPO / "io/papermc/paper/paper-api/1.21.8-R0.1-SNAPSHOT/paper-api-1.21.8-R0.1-SNAPSHOT.jar",
    M2_REPO / "io/papermc/paper/paper-api/1.21.6-R0.1-SNAPSHOT/paper-api-1.21.6-R0.1-SNAPSHOT.jar",
    M2_REPO / "io/papermc/paper/paper-api/1.20.4-R0.1-SNAPSHOT/paper-api-1.20.4-R0.1-SNAPSHOT.jar",
]

JAVADOC_DIR = Path("E:/code_cyanbukkit/CyanBukkit-MCP/knowledge/raw/paper_javadoc")
JAVADOC_DIR.mkdir(parents=True, exist_ok=True)

BUKKIT_PACKAGES = [
    "org/bukkit/",
    "org/bukkit/entity/",
    "org/bukkit/event/",
    "org/bukkit/inventory/",
    "org/bukkit/material/",
    "org/bukkit/command/",
    "org/bukkit/conversations/",
    "org/bukkit/scoreboard/",
    "org/bukkit/plugin/",
    "org/bukkit/configuration/",
    "org/bukkit/scheduler/",
    "org/bukkit/util/",
    "org/bukkit/generator/",
]

PRIORITY_ORDER = [
    "entity/", "event/", "inventory/", "material/", "command/",
    "plugin/", "configuration/", "scheduler/", "scoreboard/",
    "util/", "conversations/", "generator/",
]


def extract_class_info(jar_path: Path, class_path: str, tmpdir: str) -> Optional[Dict[str, Any]]:
    """Extract method signatures from a .class file using javap (extract to temp first)."""
    class_name = class_path.replace("/", ".").replace(".class", "")

    # Extract to temp
    dest = os.path.join(tmpdir, class_path.replace("/", "_"))
    os.makedirs(os.path.dirname(dest) if os.path.dirname(dest) else tmpdir, exist_ok=True)

    try:
        with zipfile.ZipFile(jar_path, 'r') as zf:
            zf.extract(class_path, tmpdir)

        extracted_path = os.path.join(tmpdir, class_path)

        result = subprocess.run(
            [JAVAP, '-p', extracted_path],
            capture_output=True,
            encoding='utf-8',
            errors='replace',
            timeout=10,
        )

        if result.returncode != 0:
            return None

        output = result.stdout
        methods = []

        for line in output.split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("Compiled"):
                continue
            if line == "}" or line.startswith("@") or line.startswith("deprecated"):
                continue
            if line.startswith("private static final"):
                continue
            if line.startswith("static {}"):
                continue
            if line.startswith("private final") and ";" in line:
                continue
            if line.startswith("private static"):
                continue
            if "class " in line or "interface " in line or "enum " in line:
                continue

            # Skip lines that don't look like method declarations
            if not line or line.startswith('#') or line.startswith('Compiled'):
                continue
            if line == '}' or line.startswith('@') or 'deprecated' in line:
                continue
            if 'private ' in line and not line.startswith('public ') and not line.startswith('protected ') and not line.startswith('default '):
                continue
            if 'class ' in line or 'interface ' in line or 'enum ' in line:
                continue
            if ' static {' in line or line.startswith('private static final'):
                continue
            if ' { ' in line and line.strip().endswith('}'):
                continue
            if 'throws ' not in line and line.strip().endswith(';'):
                # Might be a field, skip unless it looks like a method (has parentheses)
                if '(' not in line:
                    continue

            # Parse method: look for returnType methodName(params) pattern
            # Strategy: find the last '(' before ')' and work backwards
            paren_idx = line.rfind('(')
            if paren_idx < 0:
                continue

            # Extract params
            params = line[paren_idx+1 : line.rfind(')')]

            # Find method name: search backwards from '(' for first space
            before_paren = line[:paren_idx].strip()
            # Method name is the last word before '(' after removing modifiers
            parts = before_paren.split()
            if len(parts) < 2:
                continue

            # Method name is the last part (before any generic args)
            method_name = parts[-1]
            if not method_name or method_name in ('<init>', '<clinit>'):
                continue
            if '(' in method_name:  # malformed
                continue

            # Return type is everything before the method name
            # But we need to handle modifiers properly
            ret_part = ' '.join(parts[:-1])

            sig = f"{ret_part} {method_name}({params})"
            if 5 < len(sig) < 300:
                methods.append(sig)

        return {
            "class_name": class_name,
            "methods": methods,
            "method_count": len(methods),
        }
    except Exception:
        return None


def batch_extract_from_jar(jar_path: Path, max_classes: int = 450) -> List[Dict[str, Any]]:
    """Extract from all relevant classes in a jar."""
    results = []

    with zipfile.ZipFile(jar_path, 'r') as zf:
        class_files = []
        for name in zf.namelist():
            if not name.endswith('.class'):
                continue
            if name.startswith('com/') or name.startswith('net/') or name.startswith('io/'):
                continue
            for pkg in BUKKIT_PACKAGES:
                if name.startswith(pkg):
                    class_files.append(name)
                    break

    def get_priority(name):
        for i, pkg in enumerate(PRIORITY_ORDER):
            if pkg in name:
                return i
        return 99

    class_files.sort(key=get_priority)
    class_files = class_files[:max_classes]

    with tempfile.TemporaryDirectory() as tmpdir:
        for i, class_path in enumerate(class_files):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(class_files)}")

            info = extract_class_info(jar_path, class_path, tmpdir)
            if info and info['method_count'] > 0:
                results.append(info)

            # Clean temp between classes to avoid filling it
            if i % 20 == 19:
                for f in os.listdir(tmpdir):
                    fp = os.path.join(tmpdir, f)
                    if os.path.isfile(fp):
                        try:
                            os.remove(fp)
                        except:
                            pass

    return results


def main():
    print("Starting batch javadoc extraction from paper-api jars...")

    all_results = {}

    for jar_path in PAPER_API_JARS:
        if not jar_path.exists():
            print(f"Jar not found: {jar_path}")
            continue

        print(f"\nProcessing: {jar_path.name}")

        if "1.21.9" in str(jar_path):
            results = batch_extract_from_jar(jar_path, max_classes=500)
        elif "1.21.8" in str(jar_path) or "1.21.6" in str(jar_path):
            results = batch_extract_from_jar(jar_path, max_classes=300)
        else:
            results = batch_extract_from_jar(jar_path, max_classes=150)

        print(f"  Extracted {len(results)} classes")

        for info in results:
            cn = info['class_name']
            existing = all_results.get(cn, {"methods": []})
            if len(info['methods']) > len(existing['methods']):
                all_results[cn] = info

    print(f"\nTotal unique classes extracted: {len(all_results)}")

    saved = 0
    for class_name, info in all_results.items():
        safe_name = class_name.replace('.', '_')
        json_path = JAVADOC_DIR / f"{safe_name}.json"

        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    existing_mc = len(existing.get('methods', []))
                    new_mc = len(info['methods'])
                    if new_mc <= existing_mc:
                        continue
            except:
                pass

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        saved += 1

    print(f"New/updated files saved: {saved}")

    index = {
        "total_classes": len(all_results),
        "source_jars": [str(p) for p in PAPER_API_JARS if p.exists()],
    }
    with open(JAVADOC_DIR / "_batch_index.json", 'w', encoding='utf-8') as f:
        json.dump(index, f)


if __name__ == "__main__":
    main()