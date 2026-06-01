"""
Minimal V1-style method extraction - works well, keep it simple.
"""
import json
import re
from pathlib import Path

JAVADOC_DIR = Path(__file__).parent.parent / "knowledge" / "raw" / "paper_javadoc"


def clean_sig(sig: str) -> str:
    """Clean messy signatures."""
    sig = re.sub(r'\n+', ' ', sig)
    sig = re.sub(r'\s+', ' ', sig).strip()
    sig = re.sub(r'^>\s*', '', sig)  # leading ">"
    return sig


def extract_methods_simple(text: str) -> list:
    """Simple method extraction using multiline regex."""
    if not text or len(text) < 100:
        return []

    methods = []
    seen_sigs = set()

    # Normalize only triple+ newlines (method entry separators)
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

    # Pattern from working V1
    pattern = re.compile(
        r'([\w<>\[\],\s]+?)\s*\n+([\w$]+)\s*\n*\(\s*([^\)]*?)\s*\)\s*\n+(.{5,200}?)'
        r'(?=(?:[\w<>\[\],\s]+?\s*\n+[\w$]+\s*\n*\()|$)',
        re.MULTILINE | re.DOTALL
    )

    for m in pattern.finditer(cleaned):
        return_type = m.group(1).strip()
        method_name = m.group(2).strip()
        params_raw = m.group(3).strip()
        description = m.group(4).strip()

        if not re.match(r'^[\w$]+$', method_name):
            continue
        if len(return_type) > 100 or len(return_type) < 1:
            continue
        if return_type in {'extends', 'implements', 'interface', 'class', 'use'}:
            continue

        params = []
        if params_raw:
            for p in params_raw.split(','):
                p = p.strip()
                if p:
                    p = re.sub(r'\s+', ' ', p).strip()
                    if p:
                        params.append(p[:80])

        sig = f"{return_type} {method_name}({', '.join(params)})"
        sig = clean_sig(sig)

        if sig in seen_sigs:
            continue
        seen_sigs.add(sig)

        description = re.sub(r'\s+', ' ', description).strip()
        if description.startswith('use '):
            description = description[4:].strip()
        if len(description) > 200:
            description = description[:200].rsplit('. ', 1)[0] + '.'

        methods.append({
            "name": method_name,
            "signature": sig,
            "return_type": return_type[:60],
            "params": params,
            "description": description[:200] if description else ""
        })

        if len(methods) >= 200:
            break

    # Fallback: simple pattern if very few found
    if len(methods) < 10:
        simple = re.compile(r'([\w<>\[\]]+)\s+(\w+)\s*\(\s*([^\)]*)\s*\)\s*\n+(.{5,150}?)', re.MULTILINE)
        for m in simple.finditer(cleaned):
            rt = m.group(1).strip()
            mn = m.group(2).strip()
            if not re.match(r'^[\w$]+$', mn):
                continue
            pr = [p.strip()[:60] for p in m.group(3).split(',') if p.strip()]
            desc = re.sub(r'\s+', ' ', m.group(4).strip())[:150]
            sig2 = f"{rt} {mn}({', '.join(pr)})"
            if sig2 not in seen_sigs:
                seen_sigs.add(sig2)
                methods.append({"name": mn, "signature": clean_sig(sig2),
                               "return_type": rt[:60], "params": pr, "description": desc})

    return methods[:150]


def extract_description(text: str) -> str:
    """Extract better class description."""
    if not text:
        return ""
    for kw in ['Represents', 'Provides a', 'Interface for', 'Handler for', 'Manages']:
        idx = text.find(kw)
        if idx != -1:
            chunk = text[idx:idx+300]
            desc = re.sub(r'\n+', ' ', chunk).strip()
            desc = re.sub(r'\s+', ' ', desc).strip()
            if '.' in desc:
                result = desc[:desc.index('.')+1].strip()
                if len(result) > 20:
                    return result[:500]
            return desc[:500]
    return ""


def process():
    full_files = sorted(JAVADOC_DIR.glob("*_full.json"))
    print(f"Found {len(full_files)} _full.json files")

    for json_file in full_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            raw_text = data.get('full_text', '')
            class_name = data.get('class_name', json_file.stem.replace('_full', ''))

            methods = extract_methods_simple(raw_text)
            new_desc = extract_description(raw_text)
            old_desc = data.get('description', '')
            old_count = data.get('method_count', 0)

            final_desc = new_desc if len(new_desc) > len(old_desc) else old_desc

            data['methods'] = methods
            data['method_count'] = len(methods)
            if final_desc and len(final_desc) > len(old_desc):
                data['description'] = final_desc

            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"  {json_file.name}: {len(methods)} methods (was {old_count}), desc {len(old_desc)}->{len(final_desc)}")

        except Exception as e:
            print(f"  ERROR {json_file.name}: {e}")

    print("\nDone!")


if __name__ == "__main__":
    process()
