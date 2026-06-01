import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from cyanbukkit_mcp.crawl_pipeline import Crawl4AIPipeline


INDEX_URL = "https://www.spigotmc.org/wiki/index/"
DEFAULT_OUTPUT = PROJECT_ROOT / "knowledge" / "raw" / "crawl4ai"
WIKI_SOURCE = "spigotmc_wiki_full"


def safe_slug(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if path.startswith("wiki/"):
        path = path[5:]
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", path).strip("-")
    return slug or "index"


def extract_wiki_links(index_doc: dict[str, Any]) -> list[str]:
    links: list[str] = []
    seen = set()
    for group in ("internal", "external"):
        for item in index_doc.get("links", {}).get(group, []):
            href = item.get("href") if isinstance(item, dict) else None
            if not href:
                continue
            url = urljoin(INDEX_URL, href).split("#", 1)[0]
            parsed = urlparse(url)
            if parsed.netloc != "www.spigotmc.org":
                continue
            if not parsed.path.startswith("/wiki/"):
                continue
            if parsed.path in ("/wiki/", "/wiki/index/"):
                continue
            if url not in seen:
                seen.add(url)
                links.append(url)
    return sorted(links)


def write_mcp_docs(index_doc: dict[str, Any], pages: list[dict[str, Any]], target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    docs = []
    for page in pages:
        if not page.get("success"):
            continue
        title = page.get("title") or page.get("source_url")
        markdown = page.get("markdown", "")
        docs.append({
            "doc_id": page.get("doc_id"),
            "title": title,
            "source_url": page.get("source_url"),
            "fingerprint": page.get("fingerprint"),
            "markdown_chars": len(markdown),
        })
    payload = {
        "source": WIKI_SOURCE,
        "index_url": INDEX_URL,
        "index_doc_id": index_doc.get("doc_id"),
        "document_count": len(docs),
        "documents": docs,
        "mcp_tools": [
            "search_crawled_docs(query, source='spigotmc_wiki_full')",
            "get_crawled_doc(doc_id)",
            "search_all_knowledge(query)",
        ],
        "usage": "These Crawl4AI documents are stored under knowledge/raw/crawl4ai/spigotmc_wiki_full and are loaded by the existing MCP tools.",
    }
    with open(target, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


async def crawl_spigot_wiki(limit: int | None, concurrency: int, dry_run: bool) -> None:
    pipeline = Crawl4AIPipeline(DEFAULT_OUTPUT)
    index_doc = await pipeline.crawl_url(INDEX_URL, source=WIKI_SOURCE)
    if not index_doc.get("success"):
        raise RuntimeError(f"Failed to crawl Spigot wiki index: {index_doc.get('error')}")

    links = extract_wiki_links(index_doc)
    if limit is not None:
        links = links[:limit]

    if dry_run:
        print(f"Discovered {len(links)} Spigot wiki page URL(s)")
        for url in links:
            print(f"- {url}")
        return

    pages = await pipeline.crawl_urls(urls=links, source=WIKI_SOURCE, concurrency=concurrency)
    ok = sum(1 for page in pages if page.get("success"))
    print(f"Crawled Spigot wiki pages: {ok}/{len(pages)}")
    write_mcp_docs(index_doc, pages, DEFAULT_OUTPUT / WIKI_SOURCE / "_mcp_docs.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl the full SpigotMC wiki index into MCP-searchable Crawl4AI knowledge.")
    parser.add_argument("--limit", type=int, help="Limit discovered wiki pages for testing.")
    parser.add_argument("--concurrency", type=int, default=1, help="Crawl concurrency. Keep low for Cloudflare-protected sites.")
    parser.add_argument("--dry-run", action="store_true", help="Crawl only the index, then print discovered page URLs.")
    args = parser.parse_args()

    import asyncio
    asyncio.run(crawl_spigot_wiki(limit=args.limit, concurrency=args.concurrency, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
