#!/usr/bin/env python3
"""
简单测试 CyanBukkit-MCP 的 MCP 工具 (ASCII 版本)
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_knowledge_base():
    """测试知识库加载和搜索功能"""
    print("=== Testing CyanBukkit-MCP Knowledge Base ===")
    print()
    
    try:
        from cyanbukkit_mcp.knowledge_base import get_knowledge_base
        
        # 加载知识库
        kb = get_knowledge_base()
        print("[OK] Knowledge base loaded")
        print(f"  - Jar artifacts: {len(kb.cache)}")
        print(f"  - Javadoc classes: {len(kb.javadoc_cache)}")
        print(f"  - Wiki pages: {len(kb.wiki_cache)}")
        print(f"  - Plugin APIs: {len(kb.plugin_api_cache)}")
        print()
        
        # 测试搜索功能
        print("=== Testing Search Functions ===")
        
        # 1. 测试 search_classes (用于 search_spigot_javadoc)
        print("1. Testing search_classes('Player')...")
        results = kb.search_classes(query="Player", limit=5)
        print(f"   Found {len(results)} artifacts with 'Player' in class names")
        if results:
            for r in results[:3]:
                print(f"   - {r['artifact']}: {len(r.get('matching_classes', []))} matching classes")
        print()
        
        # 2. 测试 search_javadoc
        print("2. Testing search_javadoc('Player')...")
        javadoc_results = kb.search_javadoc(query="Player", limit=5)
        print(f"   Found {len(javadoc_results)} javadoc classes")
        if javadoc_results:
            for r in javadoc_results[:3]:
                print(f"   - {r.get('class_name', 'Unknown')}: {r.get('description', '')[:100]}...")
        print()
        
        # 3. 测试 search_wiki
        print("3. Testing search_wiki('event')...")
        wiki_results = kb.search_wiki(query="event", limit=5)
        print(f"   Found {len(wiki_results)} wiki pages")
        if wiki_results:
            for r in wiki_results[:3]:
                print(f"   - {r.get('title', 'Unknown')}: {r.get('url', '')}")
        print()

        
        # 4. 测试 get_javadoc_class
        print("4. Testing get_javadoc_class('Player')...")
        class_info = kb.get_javadoc_class("Player")
        if class_info and 'error' not in class_info:
            print(f"   [OK] Found class: {class_info.get('class_name', 'Unknown')}")
            print(f"   - Methods: {len(class_info.get('methods', []))}")
            print(f"   - Description: {class_info.get('description', '')[:200]}...")
        else:
            print(f"   [ERR] {class_info.get('error', 'Unknown error')}")
        print()
        
        # 5. 测试 list_artifacts
        print("5. Testing list_available_artifacts()...")
        artifacts = kb.list_artifacts(limit=5)
        print(f"   Found {len(artifacts)} artifacts (showing first 5)")
        for a in artifacts[:5]:
            print(f"   - {a}")
        print()
        
        print("=== All Tests Completed ===")
        return True
        
    except Exception as e:
        print(f"[ERR] Error testing knowledge base: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_server_import():
    """测试 MCP 服务器是否可以导入"""
    print("=== Testing MCP Server Import ===")
    print()
    
    try:
        from cyanbukkit_mcp import server
        print("[OK] MCP server module imported successfully")
        
        # 检查是否有 mcp 实例
        if hasattr(server, 'mcp'):
            print("[OK] FastMCP instance found")
            # 检查工具数量
            if hasattr(server.mcp, '_tool_manager') and hasattr(server.mcp._tool_manager, '_tools'):
                tool_count = len(server.mcp._tool_manager._tools)
                print(f"[OK] Found {tool_count} registered tools")
            else:
                print("[?] Cannot determine tool count (internal structure may vary)")
        else:
            print("[?] No 'mcp' instance found (might be created at runtime)")
        
        print()
        return True
        
    except Exception as e:
        print(f"[ERR] Error importing MCP server: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("CyanBukkit-MCP Autonomy Test")
    print("=" * 50)
    print()
    
    # 测试知识库
    kb_ok = test_knowledge_base()
    
    # 测试 MCP 服务器导入
    mcp_ok = test_mcp_server_import()
    
    print("=" * 50)
    if kb_ok and mcp_ok:
        print("[OK] All tests passed! CyanBukkit-MCP is ready.")
        sys.exit(0)
    else:
        print("[ERR] Some tests failed. Check the output above.")
        sys.exit(1)
