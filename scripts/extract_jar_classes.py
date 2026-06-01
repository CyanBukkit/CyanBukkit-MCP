#!/usr/bin/env python3
"""
从本地 Gradle/Maven 缓存的 jar 中提取类名列表，保存为 JSON。
用法：python extract_jar_classes.py
"""

import json
import os
import zipfile
from pathlib import Path
from collections import defaultdict

# 要扫描的本地仓库
SCAN_DIRS = [
    Path(r"C:\Users\SmallXY\.m2\repository"),
    Path(r"D:\Program Files\gradle\repo\caches"),
]

OUTPUT_DIR = Path(__file__).parent.parent / "knowledge" / "raw" / "jar_classes"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def is_interesting(jar_path: Path) -> bool:
    s = str(jar_path).lower()
    return any(g in s for g in [
        "spigot", "bukkit", "paper",
        "protocol", "placeholder", "vault",
        "sidebar", "worldedit", "brigadier",
    ])


def extract_classes(jar_path: Path) -> list:
    """从 jar 中抽取 .class 文件名（去掉 .class，保留包路径）"""
    classes = []
    try:
        with zipfile.ZipFile(jar_path, "r") as zf:
            for name in zf.namelist():
                if name.endswith(".class") and not name.startswith("META-INF"):
                    cls = name[:-6].replace("/", ".")
                    classes.append(cls)
    except Exception as e:
        print(f"  ERROR {jar_path.name}: {e}")
    return classes


def main():
    all_results = defaultdict(list)

    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            print(f"SKIP: {scan_dir}")
            continue
        print(f"Scanning: {scan_dir}")
        jar_files = list(scan_dir.rglob("*.jar"))
        print(f"  Found {len(jar_files)} jars total")

        for jar_path in jar_files:
            if not is_interesting(jar_path):
                continue
            classes = extract_classes(jar_path)
            if not classes:
                continue
            key = f"{jar_path.parent.parent.name}/{jar_path.parent.name}/{jar_path.stem}"
            entry = {
                "jar": str(jar_path),
                "artifact": key,
                "class_count": len(classes),
                "classes_sample": classes[:200],
                "truncated": len(classes) > 200,
            }
            all_results[key].append(entry)
            print(f"  OK {jar_path.name}: {len(classes)} classes")

    # 保存每个 artifact
    for artifact, entries in all_results.items():
        safe_name = artifact.replace("/", "_").replace("\\", "_")
        out_file = OUTPUT_DIR / f"{safe_name}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        print(f"Saved: {out_file}")

    # 汇总
    summary = {
        "total_jars": sum(len(v) for v in all_results.values()),
        "artifacts": list(all_results.keys()),
    }
    with open(OUTPUT_DIR / "_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nDone! Summary: {OUTPUT_DIR / '_summary.json'}")


if __name__ == "__main__":
    main()
