import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from cyanbukkit_mcp.crawl_pipeline import crawl_urls_sync


DEFAULT_PAGE_INDEX = PROJECT_ROOT / "knowledge" / "raw" / "spigotmc_wiki" / "page_index.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "knowledge" / "raw" / "crawl4ai"
WIKI_SOURCE = "spigotmc_wiki_full"


def load_urls(index_path: Path) -> list[str]:
    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    urls: list[str] = []
    seen = set()
    for section in data.values():
        section_url = section.get("url")
        if section_url and section_url not in seen:
            seen.add(section_url)
            urls.append(section_url)
        for page in section.get("pages", []):
            url = page.get("url")
            if url and url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def write_mcp_docs(output_dir: Path, source: str) -> None:
    source_dir = output_dir / source
    docs: list[dict[str, Any]] = []
    for json_file in sorted(source_dir.glob("*.json")):
        if json_file.name.startswith("_"):
            continue
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data.get("success"):
            continue
        docs.append({
            "doc_id": data.get("doc_id", json_file.stem),
            "title": data.get("title", ""),
            "source_url": data.get("source_url", ""),
            "fingerprint": data.get("fingerprint", ""),
            "markdown_chars": len(str(data.get("markdown", ""))),
        })
    payload = {
        "source": source,
        "document_count": len(docs),
        "documents": docs,
        "mcp_tools": [
            "search_crawled_docs(query, source='spigotmc_wiki_full')",
            "get_crawled_doc(doc_id)",
            "search_all_knowledge(query)",
        ],
        "usage": "Bundled Crawl4AI SpigotMC wiki documents are loaded from knowledge/raw/crawl4ai/spigotmc_wiki_full by the MCP server; users do not need to crawl them.",
    }
    with open(source_dir / "_mcp_docs.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl bundled SpigotMC wiki pages from the curated page index into MCP docs.")
    parser.add_argument("--page-index", type=Path, default=DEFAULT_PAGE_INDEX)
    parser.add_argument("--limit", type=int, help="Limit pages for testing.")
    parser.add_argument("--concurrency", type=int, default=1, help="Keep low for Cloudflare-protected sites.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    urls = load_urls(args.page_index)
    if args.limit is not None:
        urls = urls[:args.limit]

    if args.dry_run:
        print(f"Selected {len(urls)} SpigotMC wiki URL(s)")
        for url in urls:
            print(f"- {url}")
        return

    results = crawl_urls_sync(output_dir=DEFAULT_OUTPUT, urls=urls, source=WIKI_SOURCE, concurrency=args.concurrency)
    ok = sum(1 for result in results if result.get("success"))
    print(f"Crawled curated Spigot wiki pages: {ok}/{len(results)}")
    write_mcp_docs(DEFAULT_OUTPUT, WIKI_SOURCE)


if __name__ == "__main__":
    main()
