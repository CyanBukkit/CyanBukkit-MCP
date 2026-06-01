"""Fix raw paper_javadoc _full.json files with correct method counts.
The KB loads raw _full.json after processed dir, and if raw has 0 methods 
it overwrites the good 60 methods from processed. 
Solution: copy methods from processed back to raw."""
import json
import shutil
from pathlib import Path

processed = Path(r'E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\processed\full_classlists')
raw = Path(r'E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\paper_javadoc')

# Find all _full.json pairs
fixed = 0
for proc_file in processed.glob('*_full.json'):
    raw_file = raw / proc_file.name
    
    if not raw_file.exists():
        # Copy to raw
        shutil.copy(proc_file, raw_file)
        print(f"  Copied: {proc_file.name}")
        fixed += 1
        continue
    
    with open(proc_file, 'r', encoding='utf-8') as f:
        proc_data = json.load(f)
    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    proc_methods = proc_data.get('methods', [])
    raw_methods = raw_data.get('methods', [])
    
    if len(proc_methods) > len(raw_methods):
        raw_data['methods'] = proc_methods
        raw_data['method_count'] = len(proc_methods)
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        print(f"  Fixed: {proc_file.name} ({len(raw_methods)} -> {len(proc_methods)} methods)")
        fixed += 1

print(f"\nFixed {fixed} files in raw javadoc dir")