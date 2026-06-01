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

@mcp.tool
def search_crawled_docs(query: str, source: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Search Crawl4AI-crawled documentation stored in the knowledge base."""
    return kb.search_crawled_docs(query=query, source=source, limit=limit)

@mcp.tool
def get_crawled_doc(doc_id: str) -> Dict[str, Any]:
    """Get a full Crawl4AI-crawled document by id."""
    result = kb.get_crawled_doc(doc_id)
    if result:
        return result
    return {'error': f'Crawled document "{doc_id}" not found'}

@mcp.tool
def search_nms(query: str, mc_version: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Search NMS net.minecraft.server classes by name, package, or method signature."""
    return kb.search_nms(query=query, mc_version=mc_version, limit=limit)

@mcp.tool
def get_nms_class(class_name: str, mc_version: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed NMS class information for an optional Minecraft version."""
    result = kb.get_nms_class(class_name=class_name, mc_version=mc_version)
    if result:
        return result
    return {'error': f'NMS class "{class_name}" not found'}

@mcp.tool
def list_nms_versions() -> List[str]:
    """List Minecraft versions with generated NMS knowledge indexes."""
    return kb.list_nms_versions()

@mcp.tool
def search_all_knowledge(query: str, limit: int = 10) -> Dict[str, Any]:
    """Search JavaDoc, wiki, plugin API docs, Crawl4AI docs, and NMS indexes together."""
    return kb.search_all(query=query, limit=limit)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
