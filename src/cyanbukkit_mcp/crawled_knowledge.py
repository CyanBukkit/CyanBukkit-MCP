import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class CrawledKnowledgeLoader:
    def __init__(self, crawled_dir: Path):
        self.crawled_dir = Path(crawled_dir)
        self._loaded = False
        self.docs: Dict[str, Dict[str, Any]] = {}

    @property
    def has_data(self) -> bool:
        return self.crawled_dir.exists() and any(self.crawled_dir.glob("*/*.json"))

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if not self.crawled_dir.exists():
            return
        for json_file in self.crawled_dir.glob("*/*.json"):
            if json_file.name == "_index.json":
                continue
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                doc_id = data.get("doc_id", json_file.stem)
                data["doc_id"] = doc_id
                data["file"] = str(json_file)
                self.docs[doc_id] = data
            except Exception:
                continue

    def search(self, query: str, source: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        q = query.lower()
        results = []
        for doc_id, data in self.docs.items():
            if source and data.get("source") != source:
                continue
            title = str(data.get("title", ""))
            url = str(data.get("source_url", ""))
            markdown = str(data.get("markdown", ""))
            haystack = f"{title}\n{url}\n{markdown}".lower()
            score = 0
            if q in title.lower():
                score += 50
            if q in url.lower():
                score += 25
            score += haystack.count(q)
            if score > 0:
                results.append({
                    "doc_id": doc_id,
                    "source": data.get("source", ""),
                    "title": title,
                    "source_url": url,
                    "score": score,
                    "snippet": self._snippet(markdown, q),
                })
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:limit]

    def get_doc(self, doc_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_loaded()
        return self.docs.get(doc_id)

    def _snippet(self, text: str, query: str, length: int = 300) -> str:
        lower = text.lower()
        index = lower.find(query)
        if index < 0:
            return text[:length]
        start = max(0, index - 80)
        return text[start:start + length]
