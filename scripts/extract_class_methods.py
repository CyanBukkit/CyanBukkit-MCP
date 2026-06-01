#!/usr/bin/env python3
"""Extract method signatures from .class files using javap."""
import os
import subprocess
import json
from pathlib import Path

JAVAP_PATH = r"C:\Program Files\Java\jdk-1.8\bin\javap.exe"
CLASS_DIR = r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\spigot_api_extracted"
OUTPUT_FILE = r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\spigot_api_methods.json"

def extract_methods(class_file):
    """Extract public method signatures from a .class file."""
    try:
        result = subprocess.run(
            [JAVAP_PATH, "-public", str(class_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return None
        
        methods = []
        class_name = None
        lines = result.stdout.split('\n')
        
        for line in lines:
            line = line.strip()
            # Extract class name
            if line.startswith('public class') or line.startswith('public interface'):
                class_name = line.split()[2].split(' ')[0]
            # Extract method signatures
            if line.startswith('public') and '(' in line:
                # Clean up method signature
                method_sig = line.rstrip(';')
                methods.append(method_sig)
        
        return {
            'class_name': class_name,
            'methods': methods,
            'raw_output': result.stdout[:2000]  # First 2000 chars
        }
    except Exception as e:
        return None

def main():
    class_files = list(Path(CLASS_DIR).rglob("*.class"))
    print(f"Found {len(class_files)} .class files")
    
    results = {}
    count = 0
    
    for cf in class_files:
        rel_path = str(cf.relative_to(CLASS_DIR))
        data = extract_methods(cf)
        if data and data['methods']:
            results[rel_path] = data
            count += 1
            if count % 50 == 0:
                print(f"Processed {count} classes with methods...")
    
    print(f"\nTotal classes with public methods: {count}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
