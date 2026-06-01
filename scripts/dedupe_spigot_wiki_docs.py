import json
from pathlib import Path


SOURCE_DIR = Path("knowledge/raw/crawl4ai/spigotmc_wiki_full")
latest = {}
remove = []

for json_file in SOURCE_DIR.glob("*.json"):
    if json_file.name.startswith("_"):
        continue
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    url = data.get("source_url", "")
    if url in latest:
        remove.append(latest[url])
    latest[url] = json_file

for json_file in remove:
    json_file.unlink()

docs = []
for url, json_file in sorted(latest.items()):
    if json_file in remove:
        continue
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    docs.append({
        "doc_id": data.get("doc_id", json_file.stem),
        "title": data.get("title", ""),
        "source_url": url,
        "fingerprint": data.get("fingerprint", ""),
        "markdown_chars": len(str(data.get("markdown", ""))),
    })

payload = {
    "source": "spigotmc_wiki_full",
    "document_count": len(docs),
    "documents": docs,
    "mcp_tools": [
        "search_crawled_docs(query, source='spigotmc_wiki_full')",
        "get_crawled_doc(doc_id)",
        "search_all_knowledge(query)",
    ],
    "usage": "Bundled Crawl4AI SpigotMC wiki documents are loaded from knowledge/raw/crawl4ai/spigotmc_wiki_full by the MCP server; users do not need to crawl them.",
}

with open(SOURCE_DIR / "_mcp_docs.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"removed {len(remove)} duplicate files")
print(f"documents {len(docs)}")
