"""Extract enum constants for Material and Sound, and interface fields."""
import json
import re
from pathlib import Path

def extract_enum_constants(full_text: str, class_name: str) -> list:
    """Extract enum constant names from javadoc."""
    results = []
    seen = set()
    
    # Pattern: CONSTANT_NAME followed by description
    # E.g., "ACACIA_BOAT" "BlockData: Door"
    const_pattern = re.compile(r'\b([A-Z][A-Z0-9_]{2,30})\b')
    
    # Common non-constant words to exclude
    exclude = {'NULL', 'TRUE', 'FALSE', 'NULLABLE', 'NOTNULL', 'MODIFIER', 'SIGNATURE',
               'RETURN', 'PARAM', 'DESCRIPTION', 'SUMMARY', 'OVERVIEW', 'PACKAGE', 'CLASS',
               'INTERFACE', 'ENUM', 'EXTENDS', 'IMPLEMENTS', 'PUBLIC', 'PRIVATE', 'PROTECTED',
               'STATIC', 'FINAL', 'ABSTRACT', 'VOID', 'STRING', 'INT', 'BOOLEAN', 'DOUBLE',
               'FLOAT', 'LONG', 'BYTE', 'SHORT', 'CHAR', 'OBJECT', 'TYPE', 'GET', 'SET',
               'NAME', 'ID', 'KEY', 'VALUE', 'DATA', 'BLOCK', 'ITEM', 'ENTITY', 'PLAYER',
               'WORLD', 'CHUNK', 'INVENTORY', 'EVENT', 'HANDLER', 'METHOD', 'FIELD', 'CONSTANT'}
    
    for match in const_pattern.finditer(full_text):
        name = match.group(1)
        if name in exclude or name in seen:
            continue
        if name.startswith('_') or name.endswith('_'):
            continue
        
        # Valid enum constant: uppercase, separated by underscores, 3-40 chars
        if '_' in name or name.isupper():
            seen.add(name)
            results.append(name)
    
    return results[:80]  # Limit to 80 constants

def main():
    raw = Path(r'E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\paper_javadoc')
    output_dir = Path(r'E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\processed\full_classlists')
    
    special_classes = {
        'Material': 'Material',
        'Sound': 'Sound',
        'EntityType': 'EntityType',
        'PotionType': 'PotionType',
        'Statistic': 'Statistic',
    }
    
    for class_name in special_classes:
        fp = raw / f"{class_name}_full.json"
        if not fp.exists():
            print(f"Not found: {class_name}")
            continue
        
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        full_text = data.get('full_text', '')
        desc = data.get('description', '')
        existing_methods = data.get('methods', [])
        
        # Get enum constants / static fields
        constants = extract_enum_constants(full_text, class_name)
        
        print(f"{class_name}: {len(constants)} constants extracted")
        for c in constants[:10]:
            print(f"  {c}")
        
        # Append constants as "methods" for searchability
        # Format as: CONSTANT_NAME (constant) 
        new_methods = existing_methods.copy()
        for const in constants:
            sig = f"{const} (constant)"
            if sig not in new_methods:
                new_methods.append(sig)
        
        # Also add from description
        more_consts = extract_enum_constants(desc, class_name)
        for const in more_consts:
            sig = f"{const} (constant)"
            if sig not in new_methods:
                new_methods.append(sig)
        
        data['methods'] = new_methods
        data['method_count'] = len(new_methods)
        
        # Save to processed
        output_path = output_dir / f"{class_name}_full.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Also update raw
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"  -> saved {len(new_methods)} total items")

if __name__ == '__main__':
    main()