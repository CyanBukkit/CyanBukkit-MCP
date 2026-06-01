#!/usr/bin/env python3
"""
Extract FULL class lists from JAR files.
The existing JSON files only have 'classes_sample' (truncated).
This script extracts ALL classes from the actual JARs.
"""

import json
import zipfile
import os
from pathlib import Path
from typing import List, Dict, Any
import sys

def extract_classes_from_jar(jar_path: str) -> List[str]:
    """Extract all class names from a JAR file."""
    classes = []
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            for name in jar.namelist():
                if name.endswith('.class') and not name.startswith('META-INF'):
                    # Convert path to class name
                    class_name = name.replace('/', '.').replace('.class', '')
                    classes.append(class_name)
    except Exception as e:
        print(f"Error reading {jar_path}: {e}")
    return classes

def process_json_file(json_path: Path, output_dir: Path):
    """Process a single JSON file and extract full class list."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list) or len(data) == 0:
            return
        
        item = data[0]
        jar_path = item.get('jar', '')
        
        if not jar_path or not os.path.exists(jar_path):
            print(f"JAR not found: {jar_path}")
            return
        
        print(f"Processing: {item.get('artifact', 'unknown')}")
        
        # Extract all classes
        all_classes = extract_classes_from_jar(jar_path)
        
        if not all_classes:
            print(f"  No classes found in JAR")
            return
        
        # Create output JSON with FULL class list
        output_data = {
            'jar': jar_path,
            'artifact': item.get('artifact', ''),
            'class_count': len(all_classes),
            'all_classes': all_classes,  # FULL list, not truncated
            'truncated': False
        }
        
        # Save to output directory
        output_file = output_dir / json_path.name
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"  Saved {len(all_classes)} classes to {output_file.name}")
        
    except Exception as e:
        print(f"Error processing {json_path}: {e}")

def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    json_dir = project_root / "knowledge" / "raw" / "jar_classes"
    output_dir = project_root / "knowledge" / "processed" / "full_classlists"
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process all JSON files
    json_files = list(json_dir.glob("*.json"))
    json_files = [f for f in json_files if f.name != '_summary.json']
    
    print(f"Found {len(json_files)} JSON files to process")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
    
    processed = 0
    failed = 0
    
    for i, json_file in enumerate(json_files):
        print(f"\n[{i+1}/{len(json_files)}] {json_file.name}")
        try:
            process_json_file(json_file, output_dir)
            processed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1
        
        # Progress update every 10 files
        if (i + 1) % 10 == 0:
            print(f"\nProgress: {i+1}/{len(json_files)} ({(i+1)/len(json_files)*100:.1f}%)")
    
    print("\n" + "=" * 60)
    print(f"Completed: {processed} processed, {failed} failed")
    print(f"Output directory: {output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
