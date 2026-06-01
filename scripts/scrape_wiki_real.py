import os
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
import subprocess

# Paths
XB_CLI = r"D:\Program Files\QClaw\v0.2.23.532\resources\openclaw\config\skills\xbrowser\scripts\xb.cjs"
WIKI_DIR = Path(r"E:\code_cyanbukkit\CyanBukkit-MCP\knowledge\raw\spigotmc_wiki\pages")

def xb_run(cmd):
    full_cmd = f'node "{XB_CLI}" run --browser cft {cmd}'
    result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True)
    try:
        return json.loads(result.stdout)
    except:
        return {"ok": False, "error": result.stdout or result.stderr}

def scrape_page(url, page_id):
    print(f"Scraping {url}...")
    
    # Open page
    res = xb_run(f'open "{url}"')
    if not res.get("ok"):
        print(f"  Failed to open: {res.get('error')}")
        return False
        
    # Wait and get content
    xb_run('wait --load networkidle')
    
    # We use evaluate to get the innerHTML of the wiki content
    # Spigot wiki content is usually in #wikiPage or .wikiContent
    js_cmd = 'evaluate "() => document.querySelector(\'#wikiPage, .wikiContent, .messageText, article, main\')?.innerHTML || document.body.innerHTML"'
    res = xb_run(js_cmd)
    
    if not res.get("ok") or not res.get("data", {}).get("result", {}).get("success"):
        print(f"  Failed to get HTML: {res}")
        return False
        
    html = res["data"]["result"]["data"]
    soup = BeautifulSoup(html, 'html.parser')
    
    # Basic cleaning
    for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()
        
    text = soup.get_text(separator='\n', strip=True)
    
    result = {
        "title": page_id.replace("-", " ").title(),
        "url": url,
        "content": text,
        "content_length": len(text),
        "method": "xbrowser-eval"
    }
    
    out_path = WIKI_DIR / f"{page_id}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"  Saved {len(text)} chars to {out_path.name}")
    return True

def main():
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    
    # Target core pages that might be empty or missing
    targets = [
        ("bukkit-api", "https://www.spigotmc.org/wiki/bukkit-api/"),
        ("event-api", "https://www.spigotmc.org/wiki/event-api/"),
        ("spigot-configuration", "https://www.spigotmc.org/wiki/spigot-configuration/"),
        ("plugin-yml", "https://www.spigotmc.org/wiki/plugin-yml/"),
        ("spigot-maven", "https://www.spigotmc.org/wiki/spigot-maven/"),
        ("creating-a-command", "https://www.spigotmc.org/wiki/creating-a-command/"),
        ("scheduler-programming", "https://www.spigotmc.org/wiki/scheduler-programming/")
    ]
    
    for page_id, url in targets:
        scrape_page(url, page_id)
        time.sleep(1)

if __name__ == "__main__":
    main()
