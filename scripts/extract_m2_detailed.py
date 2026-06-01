import os
import json
import zipfile
from pathlib import Path

def extract_jar_info(jar_path, output_dir):
    jar_path = Path(jar_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Locate pom.xml in the jar
    pom_content = ""
    classes = []
    
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            # Look for pom.xml
            for name in jar.namelist():
                if name.endswith("pom.xml"):
                    pom_content = jar.read(name).decode('utf-8', errors='ignore')
                if name.endswith(".class"):
                    # Convert path to class name
                    class_name = name.replace("/", ".").replace(".class", "")
                    classes.append(class_name)
    except Exception as e:
        print(f"Error reading {jar_path.name}: {e}")
        return

    # Basic POM extraction (very simple regex-free approach for now)
    metadata = {
        "jar_name": jar_path.name,
        "pom_raw": pom_content,
        "classes": sorted(classes)
    }
    
    safe_name = jar_path.stem.replace(".", "_").replace("-", "_")
    output_file = output_dir / f"m2_{safe_name}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"Extracted {len(classes)} classes from {jar_path.name}")

def main():
    m2_repo = Path(r"C:\Users\SmallXY\.m2\repository")
    output_dir = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\m2_extracted")
    
    # Common Bukkit/Spigot/Paper paths
    paths = [
        m2_repo / "org/spigotmc/spigot-api",
        m2_repo / "org/bukkit/bukkit",
        m2_repo / "io/papermc/paper/paper-api"
    ]
    
    for base_path in paths:
        if not base_path.exists():
            continue
            
        print(f"Scanning {base_path}...")
        for jar in base_path.rglob("*.jar"):
            # Skip sources and javadoc jars
            if "-sources" in jar.name or "-javadoc" in jar.name:
                continue
            extract_jar_info(jar, output_dir)

if __name__ == "__main__":
    main()
