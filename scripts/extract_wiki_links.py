#!/usr/bin/env python3
"""
从已抓取的 wiki 页面中提取内部链接，发现更多页面
"""

import json
import os
import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def extract_links_from_page(html_content):
    """从 HTML 内容中提取 SpigotMC Wiki 内部链接"""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    
    # 查找所有链接
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # 匹配 SpigotMC Wiki 内部链接
        if '/wiki/' in href and 'spigotmc.org' in href:
            # 提取页面 ID
            page_id = href.split('/wiki/')[-1].split('#')[0].split('?')[0]
            if page_id and page_id not in ['index', 'Main_Page']:
                links.add(page_id)
    
    return links

def main():
    print("=== Extract Wiki Links from Existing Pages ===")
    print()
    
    # 读取已抓取的页面
    pages_dir = project_root / "knowledge" / "raw" / "spigotmc_wiki" / "pages"
    if not pages_dir.exists():
        print(f"Pages directory not found: {pages_dir}")
        return
    
    existing_pages = [f.stem for f in pages_dir.glob("*.json")]
    print(f"Existing pages: {len(existing_pages)}")
    
    # 从每个页面提取链接
    all_links = set()
    for json_file in pages_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
                if 'full_content' in page_data:
                    links = extract_links_from_page(page_data['full_content'])
                    all_links.update(links)
        except Exception as e:
            print(f"Error reading {json_file.name}: {e}")
    
    print(f"Found {len(all_links)} unique links")
    
    # 过滤掉已存在的页面
    new_links = [link for link in all_links if link not in existing_pages]
    print(f"New links to scrape: {len(new_links)}")
    
    if not new_links:
        print("No new links found!")
        return
    
    # 保存新链接列表
    output_file = project_root / "knowledge" / "raw" / "spigotmc_wiki" / "discovered_links.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for link in sorted(new_links):
            f.write(f"{link}\n")
    
    print(f"Saved new links to: {output_file}")
    
    # 尝试抓取前 10 个新页面
    print()
    print("Scraping first 10 new pages...")
    base_url = "https://www.spigotmc.org/wiki/"
    scraped_count = 0
    
    for i, page_id in enumerate(sorted(new_links)[:10]):
        page_url = f"{base_url}{page_id}"
        print(f"  {i+1}. {page_id}")
        
        try:
            response = requests.get(page_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title = soup.find('title')
                title_text = title.get_text() if title else "Unknown"
                
                content_div = soup.find('div', class_='wiki-content') or soup.find('article') or soup.find('main')
                content_text = ""
                if content_div:
                    for script in content_div(["script", "style"]):
                        script.decompose()
                    content_text = content_div.get_text(separator='\n', strip=True)
                
                # 保存
                output_json = pages_dir / f"{page_id}.json"
                page_data = {
                    'url': page_url,
                    'title': title_text,
                    'content': content_text[:5000],
                    'full_content': content_text,
                    'scraped_at': __import__('time').strftime('%Y-%m-%d %H:%M:%S')
                }
                
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(page_data, f, indent=2, ensure_ascii=False)
                
                print(f"    ✓ Saved ({len(content_text)} chars)")
                scraped_count += 1
            else:
                print(f"    ✗ HTTP {response.status_code}")
        
        except Exception as e:
            print(f"    ✗ Error: {e}")
        
        __import__('time').sleep(1)
    
    print()
    print(f"Successfully scraped {scraped_count} new pages")
    print(f"Total wiki pages: {len(existing_pages) + scraped_count}")

if __name__ == "__main__":
    main()
