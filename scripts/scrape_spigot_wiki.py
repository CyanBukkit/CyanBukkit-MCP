#!/usr/bin/env python3
"""
用 xbrowser 抓取 SpigotMC Wiki 所有页面列表和内容。
需要先启动 xbrowser:  node xb.cjs init
"""

import json
import subprocess
import time
import re
from pathlib import Path

BASE_DIR = Path(r"D:\Program Files\QClaw\v0.2.22.518\resources\openclaw\config\skills\xbrowser")
XB = str(BASE_DIR / "scripts" / "xb.cjs")
NODE = r"C:\ProgramData\miniconda3\python.exe"  # 实际是 node，但 env 变量名是 NODE

OUTPUT_DIR = Path(__file__).parent.parent / "knowledge" / "raw" / "spigotmc_wiki"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def xb_run(*args: str) -> dict:
    """调用 xb CLI，返回解析后的 JSON。"""
    cmd = [NODE, XB, "run", "--browser", "default"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"ok": False, "raw": result.stdout, "stderr": result.stderr}


def get_snapshot_refs(snapshot_data: dict) -> dict:
    """从 snapshot 结果中提取 refs。"""
    if not snapshot_data.get("ok"):
        return {}
    data = snapshot_data.get("data", {}).get("result", {})
    return data.get("refs", {})


def find_wiki_links(snapshot_data: dict) -> list[str]:
    """从 snapshot 中找出所有 Wiki 页面链接。"""
    links = []
    refs = get_snapshot_refs(snapshot_data)
    for ref_id, ref_info in refs.items():
        name = ref_info.get("name", "")
        # SpigotMC wiki 页面链接特征
        if name and len(name) > 2 and ref_info.get("role") == "link":
            links.append(name)
    return links


def main():
    print("开始抓取 SpigotMC Wiki...")

    # 1. 打开 wiki index
    print("步骤1: 打开 Wiki Index")
    r = xb_run("open", "https://www.spigotmc.org/wiki/index/")
    time.sleep(3)

    # 2. 获取快照，找到 "Page List" 链接
    print("步骤2: 获取页面快照")
    r = xb_run("snapshot", "-i")
    if not r.get("ok"):
        print(f"  ✗ snapshot 失败: {r}")
        return

    # 查找所有链接
    refs = r.get("data", {}).get("result", {}).get("refs", {})
    page_list_ref = None
    for ref_id, ref_info in refs.items():
        if "page" in ref_info.get("name", "").lower() and "list" in ref_info.get("name", "").lower():
            page_list_ref = ref_id
            break

    if not page_list_ref:
        print("  ✗ 未找到 Page List 链接，尝试直接导航")
        xb_run("open", "https://www.spigotmc.org/wiki/page-list/")
        time.sleep(3)
    else:
        print(f"  ✓ 找到 Page List: {page_list_ref}")
        xb_run("click", f"@{page_list_ref}")
        time.sleep(3)

    # 3. 获取页面列表
    print("步骤3: 获取 Wiki 页面列表")
    r = xb_run("snapshot", "-i")
    if r.get("ok"):
        snapshot = r["data"]["result"]
        # 保存快照
        with open(OUTPUT_DIR / "page_list_snapshot.json", "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        print(f"  ✓ 快照已保存，refs 数量: {len(snapshot.get('refs', {}))}")

    # 4. 截图
    print("步骤4: 截图")
    r = xb_run("screenshot", "--full")
    if r.get("ok"):
        path = r["data"]["result"]["path"]
        print(f"  ✓ 截图: {path}")

    print("\n完成！输出目录:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
