import os
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def extract_jar_info(jar_path, output_dir):
    jar_path = Path(jar_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    artifact_id = ""
    version = ""
    classes = []
    pom_content = ""

    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            # List all classes
            for name in jar.namelist():
                if name.endswith('.class'):
                    # Convert internal path to class name
                    class_name = name.replace('/', '.').replace('.class', '')
                    classes.append(class_name)
            
            # Look for POM
            for name in jar.namelist():
                if name.endswith('pom.xml'):
                    with jar.open(name) as f:
                        pom_content = f.read().decode('utf-8')
                        break
        
        # If no internal POM, look for one next to the jar
        if not pom_content:
            pom_path = jar_path.with_suffix('.pom')
            if pom_path.exists():
                with open(pom_path, 'r', encoding='utf-8') as f:
                    pom_content = f.read()

        if pom_content:
            try:
                # Remove namespaces for easier parsing
                xml_str = pom_content
                if 'xmlns' in xml_str:
                    xml_str = xml_str.split('>', 1)[1]
                    xml_str = '<project>' + xml_str.split('</project>', 1)[0] + '</project>'
                
                root = ET.fromstring(xml_str)
                artifact_id = root.findtext('.//artifactId') or ""
                version = root.findtext('.//version') or ""
            except:
                pass

        if not artifact_id:
            artifact_id = jar_path.stem

        result = {
            "artifact": artifact_id,
            "version": version,
            "jar_path": str(jar_path),
            "class_count": len(classes),
            "classes": classes,
            "pom_content": pom_content
        }

        output_file = output_dir / f"{artifact_id}_{version}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Extracted {artifact_id} {version}: {len(classes)} classes")
        return True
    except Exception as e:
        print(f"Failed to extract {jar_path}: {e}")
        return False

def main():
    m2_repo = Path(r"C:\Users\SmallXY\.m2\repository")
    output_dir = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\m2_knowledge")
    
    # Target common APIs
    targets = [
        m2_repo / "org/spigotmc/spigot-api",
        m2_repo / "io/papermc/paper/paper-api",
        m2_repo / "org/bukkit/bukkit"
    ]
    
    for target in targets:
        if not target.exists():
            continue
        
        # Find all jars in target path
        for jar_path in target.rglob("*.jar"):
            # Skip javadoc/sources
            if "javadoc" in jar_path.name or "sources" in jar_path.name:
                continue
            
            # Extract
            extract_jar_info(jar_path, output_dir)

if __name__ == "__main__":
    main()
