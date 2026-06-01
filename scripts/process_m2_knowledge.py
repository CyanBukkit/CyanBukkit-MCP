import os
import json
from pathlib import Path

def main():
    m2_dir = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\m2_knowledge")
    processed_dir = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\processed\full_classlists")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    for json_file in m2_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Simplify for processed folder
        artifact = data.get('artifact', '')
        version = data.get('version', '')
        classes = data.get('classes', [])
        
        output = {
            "artifact": artifact,
            "version": version,
            "class_count": len(classes),
            "all_classes": classes,
            "jar": data.get('jar_path', '')
        }
        
        target_name = f"{artifact}_{version}.json".replace(" ", "_")
        with open(processed_dir / target_name, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(list(m2_dir.glob('*.json')))} artifacts to processed folder.")

if __name__ == "__main__":
    main()
