from typing import Optional, List, Dict, Any
from fastmcp import FastMCP

from cyanbukkit_mcp.knowledge_base import get_knowledge_base, BukkitKnowledgeBase

mcp = FastMCP("CyanBukkit-MCP")

# Initialize knowledge base
kb: BukkitKnowledgeBase = get_knowledge_base()

@mcp.tool
def search_javadoc(query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """Search Paper/Bukkit API JavaDoc for classes, methods, and descriptions."""
    return kb.search_javadoc(query=query, limit=limit)

@mcp.tool
def get_javadoc_class(class_name: str) -> Dict[str, Any]:
    """Get full Paper/Bukkit API JavaDoc for a specific class."""
    result = kb.get_javadoc_class(class_name)
    if result:
        return result
    return {'error': f'Class "{class_name}" not found'}

@mcp.tool
def search_wiki(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search SpigotMC Wiki pages."""
    return kb.search_wiki(query=query, limit=limit)

@mcp.tool
def list_available_artifacts(limit: int = 100) -> List[str]:
    """List all available artifacts in the knowledge base."""
    return sorted(list(kb.cache.keys()))[:limit]

@mcp.tool
def get_artifact_info(artifact_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific artifact."""
    if artifact_name in kb.cache:
        info = kb.cache[artifact_name].copy()
        if 'all_classes' in info:
            info['sample_classes'] = info['all_classes'][:20]
            del info['all_classes']
        return info
    return {'error': f'Artifact "{artifact_name}" not found'}

def main():
    mcp.run()

if __name__ == "__main__":
    main()
