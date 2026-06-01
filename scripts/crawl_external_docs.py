import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from cyanbukkit_mcp.crawl_pipeline import crawl_urls_sync


DEFAULT_TARGETS = PROJECT_ROOT / "scripts" / "crawl_targets.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "knowledge" / "raw" / "crawl4ai"


def load_targets(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def select_sources(config: dict, source_name: str | None) -> list[dict]:
    sources = config.get("sources", [])
    if source_name:
        sources = [source for source in sources if source.get("name") == source_name]
    return sources


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl documentation sources into the CyanBukkit-MCP knowledge base.")
    parser.add_argument("--targets", type=Path, default=DEFAULT_TARGETS, help="Path to crawl target config JSON.")
    parser.add_argument("--source", help="Only crawl one source group from the config.")
    parser.add_argument("--url", action="append", help="Extra URL to crawl as source user_urls. Can be repeated.")
    parser.add_argument("--limit", type=int, help="Limit URLs per source.")
    parser.add_argument("--concurrency", type=int, help="Override max concurrency.")
    parser.add_argument("--dry-run", action="store_true", help="Print selected URLs without crawling.")
    args = parser.parse_args()

    config = load_targets(args.targets)
    sources = select_sources(config, args.source)
    if args.url:
        sources.append({"name": "user_urls", "urls": args.url})

    concurrency = args.concurrency or int(config.get("max_concurrency", 2))
    selected = []
    for source in sources:
        urls = list(source.get("urls", []))
        if args.limit is not None:
            urls = urls[:args.limit]
        selected.append((source.get("name", "user_urls"), urls))

    if args.dry_run:
        for name, urls in selected:
            print(f"[{name}] {len(urls)} URL(s)")
            for url in urls:
                print(f"  - {url}")
        return

    for name, urls in selected:
        if not urls:
            continue
        results = crawl_urls_sync(output_dir=DEFAULT_OUTPUT, urls=urls, source=name, limit=args.limit, concurrency=concurrency)
        ok = sum(1 for item in results if item.get("success"))
        print(f"[{name}] crawled {ok}/{len(results)} URL(s)")


if __name__ == "__main__":
    main()
