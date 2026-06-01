import os
import json
import zipfile
import xml.etree.ElementTree as ET

REPO_PATH = r"C:\Users\SmallXY\.m2\repository"
OUTPUT_DIR = r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw"

# Target artifacts
TARGETS = [
    {"name": "paper-api", "group": "io/papermc/paper", "id": "paper-api"},
    {"name": "spigot-api", "group": "org/spigotmc", "id": "spigot-api"},
    {"name": "bukkit", "group": "org/bukkit", "id": "bukkit"}
]

def extract_metadata(jar_path, pom_path):
    metadata = {"classes": [], "pom": {}}
    
    # Extract POM info
    if os.path.exists(pom_path):
        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()
            ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
            metadata["pom"]["version"] = root.findtext(".//mvn:version", namespaces=ns)
            metadata["pom"]["artifactId"] = root.findtext(".//mvn:artifactId", namespaces=ns)
            metadata["pom"]["groupId"] = root.findtext(".//mvn:groupId", namespaces=ns)
        except Exception as e:
            print(f"Error parsing POM {pom_path}: {e}")

    # Extract class list
    if os.path.exists(jar_path):
        try:
            with zipfile.ZipFile(jar_path, 'r') as jar:
                for file in jar.namelist():
                    if file.endswith(".class"):
                        metadata["classes"].append(file.replace("/", ".").replace(".class", ""))
        except Exception as e:
            print(f"Error reading JAR {jar_path}: {e}")
            
    return metadata

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for target in TARGETS:
        target_dir = os.path.join(REPO_PATH, target["group"].replace("/", os.sep), target["id"])
        if not os.path.exists(target_dir):
            continue
            
        print(f"Scanning {target['name']} in {target_dir}")
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".jar") and not file.endswith("-sources.jar") and not file.endswith("-javadoc.jar"):
                    jar_path = os.path.join(root, file)
                    pom_file = file.replace(".jar", ".pom")
                    pom_path = os.path.join(root, pom_file)
                    
                    # Heuristic: only latest or snapshots that look like main jars
                    if "SNAPSHOT" in jar_path or "R0.1" in jar_path:
                        print(f"Processing {jar_path}")
                        meta = extract_metadata(jar_path, pom_path)
                        ver = meta["pom"].get("version", "unknown")
                        out_name = f"m2_{target['id']}_{ver}.json".replace("-", "_")
                        with open(os.path.join(OUTPUT_DIR, out_name), 'w', encoding='utf-8') as f:
                            json.dump(meta, f, indent=2)

if __name__ == "__main__":
    main()
