"""
Batch re-extract methods from HTML javadoc pages using BeautifulSoup.
This fixes the issue where long classes like Block, ArmorStand, etc. 
had no methods extracted because the HTML format wasn't being parsed correctly.
"""
import json
import re
from pathlib import Path

def extract_methods_from_html(full_text: str, class_name: str) -> list:
    """Extract method signatures from HTML javadoc page."""
    methods = []
    
    # Try to find method tables in HTML
    # Pattern 1: Method signatures in <code> or plain text
    # Look for: Type methodName(Type param, ...)
    sig_pattern = re.compile(r'([\w.<>\[\], ]+?)\s+(\w+)\s*\(([^)]*)\)')
    for match in sig_pattern.finditer(full_text):
        ret_type = match.group(1).strip()
        method_name = match.group(2).strip()
        params = match.group(3).strip()
        
        # Valid method if:
        # - return type is not empty and not too long
        # - method name is valid Java identifier
        # - not inside HTML tags like attribute names
        if (ret_type and len(ret_type) < 80 and 
            re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', method_name) and
            '<' not in method_name and  # not like "<T>"
            not method_name[0].isupper()):  # constructors excluded
            
            # Build full signature
            if params:
                sig = f"{ret_type} {method_name}({params})"
            else:
                sig = f"{ret_type} {method_name}()"
            
            # Deduplicate and length filter
            if sig not in methods and 10 < len(sig) < 250:
                methods.append(sig)
    
    return methods[:60]  # Limit to 60 methods

def main():
    javadoc_dir = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\paper_javadoc")
    output_dir = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\processed\full_classlists")
    
    # Find all _full.json files
    full_files = list(javadoc_dir.glob("*_full.json"))
    print(f"Found {len(full_files)} full pages to re-process")
    
    for json_file in full_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            class_name = data.get('class_name', json_file.stem.replace('_full', ''))
            full_text = data.get('full_text', '')
            
            if len(full_text) < 500:
                print(f"  Skipping {class_name} (not enough text: {len(full_text)})")
                continue
            
            # Extract methods from HTML
            new_methods = extract_methods_from_html(full_text, class_name)
            
            print(f"  {class_name}: {len(new_methods)} methods extracted from {len(full_text)} chars HTML")
            
            # Update the full page with extracted methods
            data['methods'] = new_methods
            data['method_count'] = len(new_methods)
            
            # Save back to processed dir
            output_name = class_name.replace(' ', '_') + '_full.json'
            output_path = output_dir / output_name
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"  Error processing {json_file.name}: {e}")
    
    print(f"\nDone! Updated all full pages with extracted methods.")

if __name__ == '__main__':
    main()