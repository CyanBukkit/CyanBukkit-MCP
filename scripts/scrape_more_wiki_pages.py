#!/usr/bin/env python3
"""
抓取更多 SpigotMC Wiki 页面
"""

import json
import os
import sys
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

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

def scrape_wiki_page(page_url, output_dir):
    """抓取单个 wiki 页面"""
    try:
        print(f"Scraping: {page_url}")
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 提取页面内容
        title = soup.find('title')
        title_text = title.get_text() if title else "Unknown"
        
        # 提取主要内容
        content_div = soup.find('div', class_='wiki-content') or soup.find('article') or soup.find('main')
        content_text = ""
        if content_div:
            # 移除脚本和样式
            for script in content_div(["script", "style"]):
                script.decompose()
            content_text = content_div.get_text(separator='\n', strip=True)
        
        # 保存到 JSON
        page_id = page_url.split('/')[-1].replace('.html', '')
        output_file = output_dir / f"{page_id}.json"
        
        page_data = {
            'url': page_url,
            'title': title_text,
            'content': content_text[:5000],  # 限制长度
            'full_content': content_text,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)
        
        print(f"  Saved: {output_file.name} ({len(content_text)} chars)")
        return True
        
    except Exception as e:
        print(f"  Error scraping {page_url}: {e}")
        return False

def main():
    print("=== CyanBukkit-MCP Wiki Scraper (requests) ===")
    print()
    
    # 获取已存在的页面
    existing_pages = get_existing_pages()
    print(f"Already have {len(existing_pages)} wiki pages")
    
    # 创建输出目录
    output_dir = project_root / "knowledge" / "raw" / "spigotmc_wiki" / "pages"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # SpigotMC Wiki 基础 URL
    base_url = "https://www.spigotmc.org/wiki/"
    
    # 已知的一些重要页面（示例）
    important_pages = [
        "creating-a-plugin-description-file",
        "plugin-lifecycle",
        "plugin-configuration",
        "plugin-messaging",
        "plugin-databases",
        "plugin-permissions",
        "event-api",
        "scheduler",
        "inventory-api",
        "item-api",
        "metadata-api",
        "scoreboard-api",
        "boss-bar-api",
        "particle-api",
        "sound-api",
        "potion-effects",
        "enchantment-api",
        "world-api",
        "block-api",
        "entity-api",
        "player-api",
        "offline-player-api",
        "ban-list",
        "whitelist",
        "ops",
        "server-properties",
        "bukkityml",
        "commandsyml",
        "help-yml",
        "permissions-yml",
        "plugin-yml"
    ]
    
    # 过滤掉已存在的页面
    pages_to_scrape = [p for p in important_pages if p not in existing_pages]
    print(f"Need to scrape {len(pages_to_scrape)} more pages")
    
    if not pages_to_scrape:
        print("All important pages already scraped!")
        return
    
    # 抓取页面
    success_count = 0
    for page_id in pages_to_scrape[:20]:  # 限制数量，避免被封
        page_url = f"{base_url}{page_id}"
        if scrape_wiki_page(page_url, output_dir):
            success_count += 1
        time.sleep(1)  # 礼貌延迟
    
    print()
    print(f"Successfully scraped {success_count}/{len(pages_to_scrape[:20])} pages")
    print(f"Total wiki pages: {len(existing_pages) + success_count}")

if __name__ == "__main__":
    main()
