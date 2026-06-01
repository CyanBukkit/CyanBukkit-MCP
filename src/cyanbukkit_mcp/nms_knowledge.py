import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class NMSKnowledgeBase:
    def __init__(self, index_dir: Path, classes_dir: Path):
        self.index_dir = Path(index_dir)
        self.classes_dir = Path(classes_dir)
        self._loaded = False
        self.indexes: Dict[str, List[Dict[str, Any]]] = {}

    @property
    def has_data(self) -> bool:
        return self.index_dir.exists() and any(self.index_dir.glob("*.json"))

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if not self.index_dir.exists():
            return
        for index_file in self.index_dir.glob("*.json"):
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                version = data.get("minecraft_version", index_file.stem)
                self.indexes[version] = data.get("classes", [])
            except Exception:
                continue

    def list_versions(self) -> List[str]:
        self._ensure_loaded()
        return sorted(self.indexes.keys())

    def search(self, query: str, mc_version: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        q = query.lower()
        versions = [mc_version] if mc_version else self.list_versions()
        results = []
        for version in versions:
            for item in self.indexes.get(version, []):
                class_name = str(item.get("class_name", ""))
                short_name = str(item.get("short_name", ""))
                package = str(item.get("package", ""))
                methods = "\n".join(str(method.get("signature", method)) for method in item.get("methods", []))
                haystack = f"{class_name}\n{short_name}\n{package}\n{methods}".lower()
                score = 0
                if q == short_name.lower():
                    score += 100
                elif q in short_name.lower():
                    score += 50
                if q in class_name.lower():
                    score += 30
                score += haystack.count(q)
                if score > 0:
                    results.append({
                        "minecraft_version": version,
                        "class_name": class_name,
                        "short_name": short_name,
                        "package": package,
                        "score": score,
                        "method_count": len(item.get("methods", [])),
                        "source_jar": item.get("source_jar", ""),
                    })
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:limit]

    def get_class(self, class_name: str, mc_version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        self._ensure_loaded()
        versions = [mc_version] if mc_version else self.list_versions()
        needle = class_name.lower()
        for version in versions:
            version_dir = self.classes_dir / version
            candidates = [version_dir / f"{class_name.replace('.', '_')}.json"]
            for path in candidates:
                if path.exists():
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
            for item in self.indexes.get(version, []):
                if item.get("class_name", "").lower() == needle or item.get("short_name", "").lower() == needle:
                    return item
        return None
