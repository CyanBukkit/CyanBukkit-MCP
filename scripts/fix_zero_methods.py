"""Enhanced method extraction for edge case HTML pages."""
import json
import re
from pathlib import Path

def extract_methods_enhanced(full_text: str, class_name: str) -> list:
    """Extract method signatures with multiple patterns for tricky HTML."""
    methods = []
    seen = set()
    
    sig_pattern = re.compile(r'([\w.<>\[\], ]+?)\s+(\w+)\s*\(([^)]*)\)')
    
    # Pattern 1: Standard Java signature (returnType methodName(params))
    sig_pattern = re.compile(r'([\w.<>\[\], ]+?)\s+(\w+)\s*\(([^)]*)\)')
    for match in sig_pattern.finditer(full_text):
        ret_type = match.group(1).strip()
        method_name = match.group(2).strip()
        params = match.group(3).strip()
        
        if (ret_type and len(ret_type) < 100 and 
            re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', method_name) and
            not method_name[0].isupper() and
            '<' not in method_name and
            method_name not in ('Causes', 'Checks', 'Returns', 'This', 'Gets', 'Sets', 'A', 'The', 'If', 'See')):
            
            sig = f"{ret_type} {method_name}({params})" if params else f"{ret_type} {method_name}()"
            if sig not in seen and 10 < len(sig) < 300:
                seen.add(sig)
                methods.append(sig)
    
    # Pattern 2: Common getter/setter patterns in javadoc HTML
    getter_pattern = re.compile(r'\b(get|is|set|has)(\w+)\s*\(')
    for match in getter_pattern.finditer(full_text):
        prefix = match.group(1)
        rest = match.group(2)
        method_name = f"{prefix}{rest}"
        # Try to find return type before this
        start = max(0, match.start() - 100)
        context = full_text[start:match.end()]
        # Simple extraction
        methods.append(method_name + "()")
    
    # Pattern 3: Look for method name lists in <li> or table rows
    method_list_pattern = re.compile(r'<a[^>]*title="([^"]+)"[^>]*>\s*(\w+)\s*</a>', re.IGNORECASE)
    for match in method_list_pattern.finditer(full_text):
        method_name = match.group(2).strip()
        if re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', method_name) and not method_name[0].isupper():
            sig = f"{method_name}()"
            if sig not in seen and len(sig) > 3:
                seen.add(sig)
                methods.append(sig)
    
    # Pattern 4: Extract from decompiled method tables (Table)
    # Find lines like: getBlockInHand() or getLocation()
    simple_pattern = re.compile(r'\b(\w{4,50})\s*\(\s*\)')
    for match in simple_pattern.finditer(full_text):
        name = match.group(1)
        if (re.match(r'^[a-z][a-zA-Z0-9]*$', name) and 
            name not in seen and
            name[0].islower()):
            sig = f"{name}()"
            seen.add(sig)
            methods.append(sig)
    
    return list(dict.fromkeys(methods))[:80]

def main():
    javadoc_dir = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\paper_javadoc")
    output_dir = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\processed\full_classlists")
    
    # Target files with 0 methods
    zero_method_classes = ['Material', 'Sound', 'Tag', 'Monster', 'Spider', 'Animals']
    
    for class_name in zero_method_classes:
        # Find the _full.json file for this class
        patterns = [
            javadoc_dir / f"{class_name}_full.json",
            javadoc_dir / f"{class_name}.json",
        ]
        
        json_file = None
        for p in patterns:
            if p.exists():
                json_file = p
                break
        
        if not json_file:
            print(f"  Not found: {class_name}")
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            full_text = data.get('full_text', '')
            new_methods = extract_methods_enhanced(full_text, class_name)
            
            # Also look in methods field for the pattern
            if len(new_methods) == 0:
                desc = data.get('description', '')
                methods_field = data.get('methods', [])
                
                # Use the same sig_pattern
                sig_pat = re.compile(r'([\w.<>\[\], ]+?)\s+(\w+)\s*\(([^)]*)\)')
                
                # Check methods field
                for m in methods_field:
                    if isinstance(m, str) and '(' in m:
                        new_methods.append(m)
                    elif isinstance(m, dict):
                        name = m.get('name', '')
                        if name:
                            sig = f"{name}()"
                            if sig not in new_methods:
                                new_methods.append(sig)
                
                # Extract from description too
                if desc:
                    for match in sig_pat.finditer(desc):
                        ret_type = match.group(1).strip()
                        method_name = match.group(2).strip()
                        if re.match(r'^[a-z][a-zA-Z0-9]*$', method_name):
                            sig = f"{method_name}()"
                            if sig not in new_methods:
                                new_methods.append(sig)
            
            print(f"  {class_name}: {len(new_methods)} methods")
            for m in new_methods[:10]:
                print(f"    - {m}")
            
            # Update the data
            data['methods'] = new_methods
            data['method_count'] = len(new_methods)
            
            # Save back
            output_name = class_name.replace(' ', '_') + '_full.json'
            output_path = output_dir / output_name
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"  Error: {class_name}: {e}")

if __name__ == '__main__':
    main()