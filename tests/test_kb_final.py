import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cyanbukkit_mcp.knowledge_base import get_knowledge_base

kb = get_knowledge_base()
print("Knowledge base stats:")
print(f"  Cache: {len(kb.cache)}")
print(f"  Javadoc index: {len(kb.javadoc_index)}")
print(f"  Wiki: {len(kb.wiki_cache)}")
print(f"  Plugin API: {len(kb.plugin_api_cache)}")

# Test get_javadoc_class
result = kb.get_javadoc_class('Player')
if result:
    print(f"\nget_javadoc_class('Player'): {len(result.get('methods', []))} methods")
    print(f"  class_name: {result.get('class_name')}")
    print(f"  description (first 200): {result.get('description', '')[:200]}")
else:
    print("\nget_javadoc_class('Player'): FAILED")

# Test search_javadoc
r2 = kb.search_javadoc('Player', limit=5)
print(f"\nsearch_javadoc('Player'): {len(r2)} results")
for r in r2[:3]:
    print(f"  {r['class_name']}: score={r['score']}, {r.get('description', '')[:80]}")

# Test server import
print("\nTesting server import...")
from cyanbukkit_mcp.server import mcp
print("  MCP server loaded")