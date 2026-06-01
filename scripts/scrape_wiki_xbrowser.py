#!/usr/bin/env python3
"""
使用 xbrowser 抓取 SpigotMC Wiki 更多页面
需要 JS 渲染的页面通过 xbrowser 抓取
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def get_existing_pages():
    """获取已存在的 wiki 页面 ID 列表"""
    wiki_dir = project_root / "knowledge" / "raw" / "spigotmc_wiki" / "pages"
    if not wiki_dir.exists():
        return []
    
    existing = []
    for json_file in wiki_dir.glob("*.json"):
        existing.append(json_file.stem)
    
    return existing

def get_wiki_page_urls():
    """从 index 文件获取所有 wiki 页面 URL"""
    index_file = project_root / "knowledge" / "raw" / "spigotmc_wiki" / "page_index.json"
    if not index_file.exists():
        print(f"Index file not found: {index_file}")
        return []
    
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
            # 假设 index 是 URL 列表或包含 URL 的字典
            if isinstance(index_data, list):
                return index_data
            elif isinstance(index_data, dict):
                # 尝试提取 URL
                if 'urls' in index_data:
                    return index_data['urls']
                elif 'pages' in index_data:
                    return index_data['pages']
            return []
    except Exception as e:
        print(f"Error reading index: {e}")
        return []

def main():
    print("=== CyanBukkit-MCP Wiki Scraper (xbrowser) ===")
    print()
    
    # 获取已存在的页面
    existing_pages = get_existing_pages()
    print(f"Already have {len(existing_pages)} wiki pages")
    
    # 获取所有页面 URL
    all_urls = get_wiki_page_urls()
    print(f"Found {len(all_urls)} total URLs in index")
    
    if not all_urls:
        print("No URLs found. Please run save_wiki_index.py first.")
        return
    
    # 找出需要抓取的页面
    urls_to_scrape = []
    for url in all_urls:
        # 从 URL 提取页面 ID
        if isinstance(url, str):
            page_id = url.split('/')[-1].replace('.html', '')
        elif isinstance(url, dict) and 'url' in url:
            page_id = url['url'].split('/')[-1].replace('.html', '')
        else:
            continue
            
        if page_id not in existing_pages:
            urls_to_scrape.append(url)
    
    print(f"Need to scrape {len(urls_to_scrape)} more pages")
    
    if not urls_to_scrape:
        print("All pages already scraped!")
        return
    
    # 由于 xbrowser 需要手动操作，这里只生成需要抓取的 URL 列表
    # 实际抓取需要通过 OpenClaw xbrowser 工具完成
    output_file = project_root / "knowledge" / "raw" / "spigotmc_wiki" / "urls_to_scrape.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(urls_to_scrape, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(urls_to_scrape)} URLs to scrape: {output_file}")
    print()
    print("Next steps:")
    print("1. Use xbrowser to open each URL")
    print("2. Wait for JS rendering")
    print("3. Extract page content")
    print("4. Save as JSON to knowledge/raw/spigotmc_wiki/pages/")

if __name__ == "__main__":
    main()
