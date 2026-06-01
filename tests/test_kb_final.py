import sys
sys.path.insert(0, 'E:/code_cyanbukkit/CyanBukkit-MCP/src')
from cyanbukkit_mcp.knowledge_base import get_knowledge_base

kb = get_knowledge_base()
print("Knowledge base stats:")
print(f"  Cache: {len(kb.cache)}")
print(f"  Javadoc: {len(kb.javadoc_cache)}")
print(f"  Wiki: {len(kb.wiki_cache)}")
print(f"  Plugin API: {len(kb.plugin_api_cache)}")

# Test get_javadoc_class
result = kb.get_javadoc_class('Player')
if result:
    print(f"\nget_javadoc_class('Player'): {len(result['methods'])} methods")
    print(f"  class_name: {result['class_name']}")
    print(f"  description (first 200): {result['description'][:200]}")
else:
    print("\nget_javadoc_class('Player'): FAILED")

# Test search_javadoc
r2 = kb.search_javadoc('getHealth', limit=5)
print(f"\nsearch_javadoc('getHealth'): {len(r2)} results")
for r in r2[:3]:
    print(f"  {r['class_name']}: {len(r['matching_methods'])} matches, {r['matching_methods'][:2]}")

# Test server import
print("\nTesting server import...")
from cyanbukkit_mcp.server import mcp
print(f"  MCP server loaded, tools count: TODO (check stdio startup)")