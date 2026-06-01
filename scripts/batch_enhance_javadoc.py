"""
Run method extraction on ALL regular javadoc JSON files that have enough full_text.
Creates _full.json files for each, then runs the enhance step.
"""
import json
import re
import os
import sys
from pathlib import Path

# Import from the enhance script
sys.path.insert(0, str(Path(__file__).parent))
from enhance_javadoc_methods import extract_methods_simple, clean_sig, extract_description

JAVADOC_DIR = Path(__file__).parent.parent / "knowledge" / "raw" / "paper_javadoc"

def process():
    json_files = list(JAVADOC_DIR.glob("*.json"))
    processed = 0
    skipped = 0
    errors = 0

    # Sort by file size (largest first - most content to extract from)
    file_sizes = [(f, f.stat().st_size) for f in json_files if not f.name.startswith('_')]
    file_sizes.sort(key=lambda x: x[1], reverse=True)

    for json_file, size in file_sizes:
        name = json_file.stem

        # Skip files that already have _full.json
        full_path = JAVADOC_DIR / f"{name}_full.json"
        if full_path.exists():
            skipped += 1
            continue

        # Skip system files
        if name.startswith('_'):
            skipped += 1
            continue

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            raw_text = data.get('full_text', '')
            class_name = data.get('class_name', name)

            if len(raw_text) < 500:
                print(f"  SKIP {name}: full_text too short ({len(raw_text)} chars)")
                continue

            # Extract methods from the raw_text
            methods = extract_methods_simple(raw_text)
            new_desc = extract_description(raw_text)
            old_desc = data.get('description', '')

            # Use the better description
            final_desc = new_desc if len(new_desc) > len(old_desc) else old_desc

            # Build _full.json data
            full_data = {
                'class_name': class_name,
                'url': data.get('url', ''),
                'description': final_desc,
                'methods': methods,
                'method_count': len(methods),
                'full_text': raw_text,
            }

            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(full_data, f, ensure_ascii=False, indent=2)

            status = "OK" if len(methods) > 0 else "WARN"
            print(f"  [{status}] {name}: {len(methods)} methods extracted from {len(raw_text)} chars")
            processed += 1

            if processed >= 100:
                print("  [LIMIT] Processed 100 files, stopping for this run")
                break

        except Exception as e:
            print(f"  ERROR {name}: {e}")
            errors += 1

    print(f"\nDone! Processed: {processed}, Skipped: {skipped}, Errors: {errors}")

if __name__ == "__main__":
    process()