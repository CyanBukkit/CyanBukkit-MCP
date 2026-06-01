import sys
sys.path.insert(0, 'E:/code_cyanbukkit/CyanBukkit-MCP/src')
from cyanbukkit_mcp.knowledge_base import get_knowledge_base

kb = get_knowledge_base()

# Test get_javadoc_class
result = kb.get_javadoc_class('Player')
print(f'get_javadoc_class(Player): {len(result["methods"])} methods')
print(f'First 3:')
for m in result['methods'][:3]:
    print(f'  {m}')

# Test search_javadoc
r2 = kb.search_javadoc('getHealth', limit=5)
print(f'\nsearch_javadoc(getHealth): {len(r2)} results')
for r in r2:
    print(f'  {r["class_name"]}: mc={r["method_count"]}, matches={r["matching_methods"][:2]}')

# Test search for a method that should definitely match
r3 = kb.search_javadoc('sendMessage', limit=5)
print(f'\nsearch_javadoc(sendMessage): {len(r3)} results')
for r in r3[:3]:
    print(f'  {r["class_name"]}: mc={r["method_count"]}, matches={r["matching_methods"][:2]}')

# Test Entity
r4 = kb.search_javadoc('getLocation', limit=5)
print(f'\nsearch_javadoc(getLocation): {len(r4)} results')
for r in r4[:3]:
    print(f'  {r["class_name"]}: mc={r["method_count"]}, matches={r["matching_methods"][:2]}')