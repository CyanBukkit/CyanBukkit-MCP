"""Batch scrape SpigotMC Wiki pages using requests + BeautifulSoup."""
import json
import os
import time
import re
import sys

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing requests and beautifulsoup4...")
    os.system(f"{sys.executable} -m pip install requests beautifulsoup4 -q")
    import requests
    from bs4 import BeautifulSoup

WIKI_DIR = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'raw', 'spigotmc_wiki', 'pages')
INDEX_FILE = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'raw', 'spigotmc_wiki', 'page_index.json')

HEADERS = {
    'User-Agent': 'CyanBukkit-MCP/0.1 (Knowledge indexer; +https://github.com/cyanbukkit)',
    'Accept': 'text/html',
}

def extract_wiki_content(html: str, url: str) -> dict:
    """Extract main wiki content from SpigotMC HTML page."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get title
    title_el = soup.select_one('.wikiTitle h1, .titleBar h1, h1.p-title-value')
    title = title_el.get_text(strip=True) if title_el else ''
    
    # Get main wiki content div
    content_el = soup.select_one('#wikiPage, .wikiContent, .messageText')
    if not content_el:
        # Fallback: try article/main
        content_el = soup.select_one('article, main, .content')
    
    if not content_el:
        return {'title': title, 'url': url, 'content': '', 'raw_length': len(html), 'method': 'no-content-div'}
    
    # Clean: remove script, style, nav
    for tag in content_el.find_all(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()
    
    # Get text with structure
    text = content_el.get_text(separator='\n', strip=True)
    
    # Clean up excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return {
        'title': title,
        'url': url,
        'content': text,
        'content_length': len(text),
        'method': 'bs4'
    }


def main():
    os.makedirs(WIKI_DIR, exist_ok=True)
    
    # Load page index
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    # Find existing pages
    existing = {f.replace('.json', '') for f in os.listdir(WIKI_DIR) if f.endswith('.json')}
    
    # Collect pages to scrape
    to_scrape = []
    for cat, data in index.items():
        for page in data.get('pages', []):
            url = page['url'].rstrip('/')
            page_id = url.split('/wiki/')[-1].rstrip('/')
            if page_id not in existing:
                to_scrape.append((page_id, page['name'], page['url']))
    
    print(f"Existing: {len(existing)}, To scrape: {len(to_scrape)}")
    
    success = 0
    failed = []
    
    for i, (page_id, name, url) in enumerate(to_scrape):
        print(f"[{i+1}/{len(to_scrape)}] Scraping: {page_id} ({name})...")
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            
            result = extract_wiki_content(resp.text, url)
            
            if not result['content'] or len(result['content']) < 50:
                print(f"  WARNING: Very short content ({len(result['content'])} chars), might be JS-rendered")
                failed.append((page_id, 'short-content'))
                # Still save it - might have something
            else:
                print(f"  OK: {result['content_length']} chars")
                success += 1
            
            # Save
            out_path = os.path.join(WIKI_DIR, f"{page_id}.json")
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            time.sleep(1.5)  # Be polite
            
        except Exception as e:
            print(f"  ERROR: {e}")
            failed.append((page_id, str(e)))
            time.sleep(2)
    
    print(f"\nDone! Success: {success}, Failed: {len(failed)}")
    if failed:
        print("Failed pages:")
        for pid, reason in failed:
            print(f"  {pid}: {reason}")


if __name__ == '__main__':
    main()
