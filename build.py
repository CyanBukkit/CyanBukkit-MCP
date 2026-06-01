import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
GENERATED_ENTRYPOINT = PROJECT_ROOT / "build_entrypoint.py"
GENERATED_ICON = ASSETS_DIR / "icon.ico"
DEFAULT_ICO = Path(r"F:\综合图片库\青桐桶\108_16x16.ico")
DEFAULT_PNG = Path(r"F:\综合图片库\青桐桶\28.png")
CONDA_PREFIX = Path(os.environ.get("CONDA_PREFIX", ""))
OPENSSL_DLLS = [
    CONDA_PREFIX / "Library" / "bin" / "libssl-3-x64.dll",
    CONDA_PREFIX / "Library" / "bin" / "libcrypto-3-x64.dll",
]


ENTRYPOINT_CODE = """from cyanbukkit_mcp.server import main\n\nif __name__ == \"__main__\":\n    main()\n"""


def _convert_png_to_ico(source: Path, target: Path) -> Path:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("PNG 图标需要 Pillow：conda run -n mcpmaker pip install pillow") from exc

    target.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(source)
    image.save(target, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
    return target


def prepare_icon(icon_path: Path | None) -> Path | None:
    source = icon_path
    if source is None:
        source = DEFAULT_ICO if DEFAULT_ICO.exists() else DEFAULT_PNG

    if not source.exists():
        print(f"Warning: icon not found: {source}")
        return None

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    if source.suffix.lower() == ".ico":
        shutil.copy2(source, GENERATED_ICON)
        return GENERATED_ICON

    if source.suffix.lower() == ".png":
        return _convert_png_to_ico(source, GENERATED_ICON)

    print(f"Warning: unsupported icon format: {source}")
    return None


def build_exe(icon: Path | None, onefile: bool) -> None:
    GENERATED_ENTRYPOINT.write_text(ENTRYPOINT_CODE, encoding="utf-8")

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "cyanbukkit-mcp",
        "--clean",
        "--noconfirm",
        "--console",
        "--paths",
        str(SRC_DIR),
        "--copy-metadata",
        "fastmcp",
        "--copy-metadata",
        "fastmcp-slim",
    ]

    if onefile:
        command.append("--onefile")

    if icon is not None:
        command.extend(["--icon", str(icon)])

    for dll in OPENSSL_DLLS:
        if dll.exists():
            command.extend(["--add-binary", f"{dll};."])

    command.append(str(GENERATED_ENTRYPOINT))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build CyanBukkit-MCP stdio executable.")
    parser.add_argument("--icon", type=Path, help="Path to .ico or .png icon. Defaults to the configured 青桐桶 icon.")
    parser.add_argument("--onedir", action="store_true", help="Build dist/cyanbukkit-mcp/ instead of one exe file.")
    args = parser.parse_args()

    if os.environ.get("CONDA_DEFAULT_ENV") != "mcpmaker":
        print("Warning: current Conda env is not mcpmaker. Recommended: conda run -n mcpmaker python build.py")

    icon = prepare_icon(args.icon)
    build_exe(icon=icon, onefile=not args.onedir)
    print("Build complete: dist/cyanbukkit-mcp.exe")


if __name__ == "__main__":
    main()
