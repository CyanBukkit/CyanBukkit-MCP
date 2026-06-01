#!/usr/bin/env python3
"""
Batch scrape remaining SpigotMC Wiki pages using xbrowser.
Reads page_index.json, checks which pages are already saved,
then scrapes unsaved pages via xbrowser.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
PAGE_INDEX = PROJECT_ROOT / "knowledge" / "raw" / "spigotmc_wiki" / "page_index.json"
PAGES_DIR = PROJECT_ROOT / "knowledge" / "raw" / "spigotmc_wiki" / "pages"

def load_page_index():
    """Load page index from JSON."""
    with open(PAGE_INDEX, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_saved_pages():
    """Get list of already saved page IDs."""
    saved = set()
    if PAGES_DIR.exists():
        for f in PAGES_DIR.glob("*.json"):
            # Extract page_id from filename (remove .json)
            page_id = f.stem
            saved.add(page_id)
    return saved

def get_unsaved_pages(page_index, saved):
    """Get list of unsaved pages."""
    unsaved = []
    for category, data in page_index.items():
        for page in data["pages"]:
            # Extract page_id from URL
            url = page["url"]
            page_id = url.rstrip("/").split("/")[-1]
            if page_id not in saved:
                unsaved.append({
                    "id": page_id,
                    "name": page["name"],
                    "url": url
                })
    return unsaved

def scrape_page_xbrowser(page_url, page_id):
    """Scrape a single page using xbrowser via subprocess."""
    # Use OpenClaw's xbrowser through CLI
    # We'll create a temp script that xbrowser will execute
    
    temp_script = PAGES_DIR.parent / f"temp_scrape_{page_id}.py"
    
    script_content = f'''
import json
import sys

# This script will be executed in the xbrowser context
# For now, we'll use a simpler approach: call xbrowser via subprocess

import subprocess
import time

# Navigate to page
result = subprocess.run(
    ["openclaw", "xbrowser", "open", "--url", "{page_url}"],
    capture_output=True,
    text=True
)
print(result.stdout)
time.sleep(2)

# Get page content
result = subprocess.run(
    ["openclaw", "xbrowser", "snapshot", "--format", "markdown"],
    capture_output=True,
    text=True
)
content = result.stdout

# Save to JSON
output = {{
    "id": "{page_id}",
    "url": "{page_url}",
    "title": "",
    "content": content,
    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
}}

output_path = r"{PAGES_DIR.as_posix()}\{page_id}.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Saved: {{output_path}}")
'''
    
    with open(temp_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"  Created temp script: {temp_script}")
    print(f"  TODO: Execute this via xbrowser (requires OpenClaw xbrowser integration)")
    
    # Clean up temp script
    # temp_script.unlink()
    
    return False  # Not yet implemented

def main():
    print("=" * 60)
    print("CyanBukkit-MCP: Batch Wiki Page Scraper")
    print("=" * 60)
    
    # Load page index
    print(f"\n[1/4] Loading page index from {PAGE_INDEX}...")
    page_index = load_page_index()
    
    # Count total pages
    total = sum(len(data["pages"]) for data in page_index.values())
    print(f"  Found {total} total pages in index")
    
    # Get saved pages
    print(f"\n[2/4] Checking already saved pages...")
    saved = get_saved_pages()
    print(f"  Already saved: {len(saved)} pages")
    print(f"  Saved: {', '.join(sorted(saved)[:5])}...")
    
    # Get unsaved pages
    print(f"\n[3/4] Identifying unsaved pages...")
    unsaved = get_unsaved_pages(page_index, saved)
    print(f"  Unsaved: {len(unsaved)} pages")
    
    if not unsaved:
        print("\n✓ All pages already scraped!")
        return
    
    # Show unsaved pages
    print(f"\n[4/4] Unsaved pages:")
    for i, page in enumerate(unsaved[:10], 1):  # Show first 10
        print(f"  {i}. {page['name']} ({page['id']})")
    if len(unsaved) > 10:
        print(f"  ... and {len(unsaved) - 10} more")
    
    # Save unsaved list for reference
    unsaved_list_path = PAGES_DIR.parent / "unsaved_pages.json"
    with open(unsaved_list_path, 'w', encoding='utf-8') as f:
        json.dump(unsaved, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved unsaved page list to: {unsaved_list_path}")
    
    print("\n" + "=" * 60)
    print("TODO: Implement xbrowser integration for batch scraping")
    print("="* 60)
    print("\nNext steps:")
    print("1. Use xbrowser to navigate to each unsaved page")
    print("2. Extract page content (markdown or text)")
    print("3. Save as JSON to pages/ directory")
    print("\nOR: Run manual xbrowser commands for each page")
    print("="* 60)

if __name__ == "__main__":
    main()
