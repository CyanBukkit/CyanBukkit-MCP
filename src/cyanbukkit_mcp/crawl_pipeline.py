import asyncio
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse


class Crawl4AINotInstalled(RuntimeError):
    pass


def safe_name(value: str, max_length: int = 80) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    if not cleaned:
        cleaned = "document"
    return cleaned[:max_length]


def fingerprint_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


class Crawl4AIPipeline:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)

    async def crawl_url(self, url: str, source: str = "user_urls", extraction_prompt: Optional[str] = None) -> Dict[str, Any]:
        try:
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        except ImportError as exc:
            raise Crawl4AINotInstalled("crawl4ai is not installed. Install with: pip install -e .[crawl]") from exc

        browser_config = BrowserConfig(
            headless=True,
            enable_stealth=True,
            user_agent_mode="random",
            viewport_width=1365,
            viewport_height=768,
        )
        config = CrawlerRunConfig(
            page_timeout=60000,
            wait_until="networkidle",
            delay_before_return_html=1.0,
            remove_overlay_elements=True,
            remove_consent_popups=True,
            simulate_user=True,
            override_navigator=True,
            magic=True,
        )
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=config)

        if not result.success:
            return {
                "success": False,
                "source": source,
                "source_url": url,
                "error": getattr(result, "error_message", "crawl failed"),
            }

        markdown = str(result.markdown or "")
        metadata = dict(result.metadata or {})
        document = {
            "success": True,
            "source": source,
            "source_url": url,
            "title": metadata.get("title") or url,
            "markdown": markdown,
            "links": result.links or {},
            "metadata": metadata,
            "extraction_prompt": extraction_prompt,
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "fingerprint": fingerprint_text(markdown),
        }
        document["doc_id"] = self.save_document(document, source)
        return document

    async def crawl_urls(self, urls: Iterable[str], source: str = "user_urls", limit: Optional[int] = None, concurrency: int = 2) -> List[Dict[str, Any]]:
        selected = list(urls)
        if limit is not None:
            selected = selected[:limit]
        semaphore = asyncio.Semaphore(max(1, concurrency))

        async def run(url: str) -> Dict[str, Any]:
            async with semaphore:
                return await self.crawl_url(url=url, source=source)

        return await asyncio.gather(*(run(url) for url in selected))

    def save_document(self, document: Dict[str, Any], source: str) -> str:
        source_dir = self.output_dir / safe_name(source)
        source_dir.mkdir(parents=True, exist_ok=True)
        parsed = urlparse(document["source_url"])
        base = safe_name(parsed.netloc + parsed.path)
        doc_id = f"{safe_name(source)}_{base}_{document['fingerprint'][:12]}"
        target = source_dir / f"{doc_id}.json"
        with open(target, "w", encoding="utf-8") as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
        self._update_index(source_dir)
        return doc_id

    def _update_index(self, source_dir: Path) -> None:
        entries = []
        for json_file in sorted(source_dir.glob("*.json")):
            if json_file.name == "_index.json":
                continue
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                entries.append({
                    "doc_id": data.get("doc_id", json_file.stem),
                    "title": data.get("title", json_file.stem),
                    "source_url": data.get("source_url", ""),
                    "file": json_file.name,
                    "fingerprint": data.get("fingerprint", ""),
                })
            except Exception:
                continue
        with open(source_dir / "_index.json", "w", encoding="utf-8") as f:
            json.dump({"documents": entries}, f, ensure_ascii=False, indent=2)


def crawl_urls_sync(output_dir: Path, urls: Iterable[str], source: str, limit: Optional[int] = None, concurrency: int = 2) -> List[Dict[str, Any]]:
    pipeline = Crawl4AIPipeline(output_dir=output_dir)
    return asyncio.run(pipeline.crawl_urls(urls=urls, source=source, limit=limit, concurrency=concurrency))
