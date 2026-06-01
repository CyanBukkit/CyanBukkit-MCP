import os
import json
from pathlib import Path

def main():
    javadoc_dir = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\paper_javadoc")
    processed_dir = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\processed\javadoc_index")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    index = []
    
    for json_file in javadoc_dir.glob("*.json"):
        if json_file.name.startswith('_'): continue
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            class_name = data.get('class_name', json_file.stem)
            description = data.get('description', '')
            methods = data.get('methods', [])
            
            # Simple summary for search
            index.append({
                "class_name": class_name,
                "short_name": class_name.split('.')[-1],
                "description": description[:300],
                "method_count": len(methods),
                "methods": [m.get('name') for m in methods[:10]],
                "file": str(json_file.name)
            })
        except:
            pass
            
    with open(processed_dir / "master_index.json", "w", encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        
    print(f"Indexed {len(index)} javadoc classes.")

if __name__ == "__main__":
    main()
