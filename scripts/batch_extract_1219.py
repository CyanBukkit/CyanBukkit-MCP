"""
Quick run: extract only from 1.21.9 jar (most important version)
"""
import zipfile, tempfile, subprocess, os, re, json
from pathlib import Path

JAVAP = r"C:\Program Files\Java\jdk-11\bin\javap.exe"
JAR = Path(r"C:\Users\SmallXY\.m2\repository\io\papermc\paper\paper-api\1.21.9-R0.1-SNAPSHOT\paper-api-1.21.9-R0.1-SNAPSHOT.jar")
JAVADOC_DIR = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\paper_javadoc")

BUKKIT_PACKAGES = [
    "org/bukkit/", "org/bukkit/entity/", "org/bukkit/event/",
    "org/bukkit/inventory/", "org/bukkit/material/", "org/bukkit/command/",
    "org/bukkit/conversations/", "org/bukkit/scoreboard/", "org/bukkit/plugin/",
    "org/bukkit/configuration/", "org/bukkit/scheduler/", "org/bukkit/util/",
    "org/bukkit/generator/",
]
PRIORITY_ORDER = ["entity/", "event/", "inventory/", "material/", "command/",
                  "plugin/", "configuration/", "scheduler/", "scoreboard/",
                  "util/", "conversations/", "generator/"]

def extract_class_info(class_path, jar_path, tmpdir):
    class_name = class_path.replace("/", ".").replace(".class", "")
    with zipfile.ZipFile(jar_path, 'r') as zf:
        zf.extract(class_path, tmpdir)
    ep = os.path.join(tmpdir, class_path)
    result = subprocess.run([JAVAP, '-p', ep], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
    if result.returncode != 0:
        return None

    methods = []
    for line in result.stdout.split("\n"):
        line = line.strip()
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
        if ' throws ' not in line and line.strip().endswith(';'):
            if '(' not in line:
                continue

        paren_idx = line.rfind('(')
        if paren_idx < 0:
            continue
        params = line[paren_idx+1 : line.rfind(')')]
        before_paren = line[:paren_idx].strip()
        parts = before_paren.split()
        if len(parts) < 2:
            continue
        method_name = parts[-1]
        if not method_name or method_name in ('<init>', '<clinit>'):
            continue
        if '(' in method_name:
            continue
        ret_part = ' '.join(parts[:-1])
        sig = f"{ret_part} {method_name}({params})"
        if 5 < len(sig) < 300:
            methods.append(sig)

    return {"class_name": class_name, "methods": methods, "method_count": len(methods)}

# List classes from jar
with zipfile.ZipFile(JAR, 'r') as zf:
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
print(f"Total classes to process: {len(class_files)}")

# Extract all classes
all_results = {}
with tempfile.TemporaryDirectory() as tmpdir:
    for i, class_path in enumerate(class_files):
        if i % 100 == 0:
            print(f"Progress: {i}/{len(class_files)}")

        info = extract_class_info(class_path, JAR, tmpdir)
        if info and info['method_count'] > 0:
            cn = info['class_name']
            existing = all_results.get(cn, {"methods": []})
            if len(info['methods']) > len(existing['methods']):
                all_results[cn] = info

print(f"Extracted {len(all_results)} classes")

# Save to files
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

print(f"Saved/updated {saved} files")