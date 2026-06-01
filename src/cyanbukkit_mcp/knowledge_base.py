import os
import sys
import json
import glob
from typing import Optional, List, Dict, Any
from pathlib import Path


class BukkitKnowledgeBase:
    """Manages the knowledge base of Bukkit/Spigot/Paper API information and SpigotMC Wiki."""
    
    def __init__(self, knowledge_dir: str = None, use_processed: bool = True):
        # Base project root
        if getattr(sys, "frozen", False):
            self.project_root = Path(sys.executable).resolve().parent
        else:
            self.project_root = Path(__file__).resolve().parents[2]
        if knowledge_dir:
            self.project_root = Path(knowledge_dir).resolve()
        
        # Paths based on the project structure
        self.raw_knowledge_dir = self.project_root / "knowledge" / "raw"
        self.processed_knowledge_dir = self.project_root / "knowledge" / "processed"
        
        if use_processed:
            self.knowledge_dir = self.processed_knowledge_dir / "full_classlists"
        else:
            self.knowledge_dir = self.raw_knowledge_dir
            
        self.wiki_dir = self.raw_knowledge_dir / "spigotmc_wiki" / "pages"
        self.javadoc_dir = self.raw_knowledge_dir / "paper_javadoc"
        self.javadoc_index_file = self.processed_knowledge_dir / "javadoc_index" / "master_index.json"
        self.plugin_apis_dir = self.raw_knowledge_dir / "plugin_apis"
        
        self.cache = {}
        self.wiki_cache = {}
        self.javadoc_cache = {}
        self.javadoc_index = []
        self.plugin_api_cache = {}
        
        # Ensure directories exist
        for d in [self.knowledge_dir, self.wiki_dir, self.javadoc_dir, self.plugin_apis_dir]:
            if not d.exists():
                d.mkdir(parents=True, exist_ok=True)
                
        self._load_all_metadata()
        self._load_wiki_pages()
        self._load_javadoc_index()
        self._load_plugin_apis()
        
        print(f"Knowledge base initialized.")
        print(f"Artifacts loaded: {len(self.cache)}")
        print(f"Wiki pages loaded: {len(self.wiki_cache)}")
        print(f"Javadoc classes indexed: {len(self.javadoc_index)}")
        print(f"Plugin API docs loaded: {len(self.plugin_api_cache)}")
    
    def _load_all_metadata(self):
        """Load metadata from all JSON files in the knowledge directory."""
        json_files = list(self.knowledge_dir.glob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if isinstance(data, dict):
                        artifact_name = data.get('artifact', json_file.stem)
                        # We might have m2_ artifacts here
                        if 'pom' in data and 'classes' in data:
                            artifact_name = data['pom'].get('artifactId', json_file.stem)
                            self.cache[json_file.stem] = {
                                'file': str(json_file),
                                'class_count': len(data.get('classes', [])),
                                'all_classes': data.get('classes', []),
                                'artifact': artifact_id,
                                'version': data['pom'].get('version', '')
                            }
                        else:
                            self.cache[artifact_name] = {
                                'file': str(json_file),
                                'class_count': data.get('class_count', 0),
                                'all_classes': data.get('all_classes', []),
                                'artifact': data.get('artifact', ''),
                                'jar': data.get('jar', ''),
                                'truncated': data.get('truncated', False)
                            }
            except Exception as e:
                # print(f"Warning: Could not load metadata {json_file.name}: {e}")
                pass
    
    def _load_wiki_pages(self):
        """Load wiki pages from raw directory."""
        for json_file in self.wiki_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    page_id = json_file.stem
                    self.wiki_cache[page_id] = {
                        'title': data.get('title', page_id),
                        'url': data.get('url', ''),
                        'content': data.get('content', str(data)) # Some are snapshots
                    }
            except Exception as e:
                pass

    def _load_javadoc_index(self):
        """Load javadoc index for faster searching."""
        if self.javadoc_index_file.exists():
            try:
                with open(self.javadoc_index_file, 'r', encoding='utf-8') as f:
                    self.javadoc_index = json.load(f)
            except Exception as e:
                print(f"Error loading javadoc index: {e}")

    def _load_plugin_apis(self):
        """Load external plugin API info."""
        for json_file in self.plugin_apis_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    name = json_file.stem
                    self.plugin_api_cache[name] = data
            except Exception:
                pass

    def get_javadoc_class(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Get full javadoc for a specific class."""
        # Try exact match or find in index
        target_file = None
        for item in self.javadoc_index:
            if item['class_name'] == class_name or item['short_name'] == class_name:
                target_file = self.javadoc_dir / item['file']
                break
        
        if not target_file:
            # Try direct file probe
            potential = self.javadoc_dir / f"{class_name.replace('.', '_')}.json"
            if potential.exists():
                target_file = potential
        
        if target_file and target_file.exists():
            with open(target_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def search_javadoc(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        results = []
        q = query.lower()
        for item in self.javadoc_index:
            score = 0
            name = item['class_name'].lower()
            short_name = item['short_name'].lower()
            
            if q == short_name: score += 100
            elif q in short_name: score += 50
            elif q in name: score += 30
            
            desc = item.get('description', '').lower()
            if q in desc: score += 10
            
            if score > 0:
                results.append({
                    'class_name': item['class_name'],
                    'short_name': item['short_name'],
                    'score': score,
                    'description': item.get('description', '')[:200]
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    def search_wiki(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        q = query.lower()
        for pid, data in self.wiki_cache.items():
            score = 0
            title = data.get('title', '').lower()
            content = data.get('content', '').lower()
            if q in title: score += 50
            score += content.count(q)
            
            if score > 0:
                results.append({
                    'page_id': pid,
                    'title': data['title'],
                    'score': score,
                    'url': data['url']
                })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]


    def search_plugin_apis(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search plugin API documentation."""
        results = []
        q = query.lower()
        for name, data in self.plugin_api_cache.items():
            score = 0
            # Match on plugin name
            if q in name.lower(): score += 50
            # Match on description
            desc = data.get('description', '').lower()
            if q in desc: score += 20
            # Match on section titles
            for sec in data.get('sections', []):
                title = sec.get('title', '').lower()
                content = sec.get('content', '').lower()
                if q in title: score += 30
                if q in content: score += content.count(q)
            
            if score > 0:
                results.append({
                    'plugin': name,
                    'score': score,
                    'description': data.get('description', '')[:200],
                    'sections_matched': sum(1 for sec in data.get('sections', []) 
                                           if q in sec.get('title', '').lower() or q in sec.get('content', '').lower())
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def get_plugin_api_detail(self, plugin_name: str, section_title: str = None) -> Optional[Dict[str, Any]]:
        """Get detailed plugin API documentation."""
        # Exact match first
        if plugin_name in self.plugin_api_cache:
            data = self.plugin_api_cache[plugin_name]
        else:
            # Fuzzy match
            for name in self.plugin_api_cache:
                if plugin_name.lower() in name.lower() or name.lower() in plugin_name.lower():
                    data = self.plugin_api_cache[name]
                    plugin_name = name
                    break
            else:
                return None
        
        result = {
            'plugin': plugin_name,
            'version': data.get('version', 'unknown'),
            'description': data.get('description', ''),
            'source_url': data.get('source_url', ''),
            'artifact': data.get('artifact', ''),
            'platform': data.get('platform', ''),
            'total_sections': data.get('section_count', len(data.get('sections', [])))
        }
        
        if section_title:
            q = section_title.lower()
            matched = [s for s in data.get('sections', []) 
                      if q in s.get('title', '').lower()]
            result['sections'] = matched[:10]
        else:
            result['sections'] = data.get('sections', [])[:20]
        
        return result


_kb_instance = None
def get_knowledge_base() -> BukkitKnowledgeBase:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = BukkitKnowledgeBase()
    return _kb_instance
