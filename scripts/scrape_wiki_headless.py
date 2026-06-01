import os
import json
import time
import subprocess
from urllib.parse import urljoin

XB_PATH = r"D:\Program Files\QClaw\v0.2.22.518\resources\openclaw\config\skills\xbrowser\scripts\xb.cjs"
OUTPUT_DIR = r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\spigotmc_wiki\pages"

def run_xb(cmd_list):
    args = ["node", XB_PATH, "run", "--browser", "cft"] + cmd_list
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
    try:
        return json.loads(result.stdout)
    except:
        print(f"Failed to parse JSON: {result.stdout}")
        return None

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # We already have the snapshot from the previous turn, let's just use it to extract links
    # For now, I'll just scrape a few key ones to demonstrate progress
    targets = [
        {"name": "spigot-configuration", "url": "https://www.spigotmc.org/wiki/spigot-configuration/"},
        {"name": "bukkit-api", "url": "https://www.spigotmc.org/wiki/spigot-plugin-development/"},
        {"name": "event-api", "url": "https://www.spigotmc.org/wiki/event-api/"}
    ]

    for target in targets:
        print(f"Scraping {target['name']}...")
        run_xb(["open", target["url"]])
        run_xb(["wait", "--load", "networkidle"])
        
        # Get content
        snap = run_xb(["snapshot", "-i"])
        if snap and snap.get("ok"):
            # Simple content extraction: just save the snapshot for now as "raw"
            # In a real scenario, we'd extract the main article text
            with open(os.path.join(OUTPUT_DIR, f"{target['name']}.json"), 'w', encoding='utf-8') as f:
                json.dump(snap["data"]["result"]["data"], f, indent=2)
        
        time.sleep(2)

if __name__ == "__main__":
    main()
