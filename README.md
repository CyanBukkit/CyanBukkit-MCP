# CyanBukkit-MCP

CyanBukkit-MCP 是面向 Minecraft Java 服务端生态的 MCP（Model Context Protocol）服务。它把 Bukkit/Spigot/Paper、NMS、ProtocolLib、PlaceholderAPI、Vault 等资料整理成 AI Agent 可以直接调用的 stdio MCP 工具。

## 最傻瓜式使用：直接调用 exe

1. 获取或构建 `dist\cyanbukkit-mcp.exe`。
2. 在 MCP 客户端里把 `command` 指向这个 exe 的绝对路径。
3. 不需要额外参数，传输方式使用 stdio。

示例：

```json
{
  "mcpServers": {
    "cyanbukkit": {
      "command": "G:\\Ai_Agent\\CyanBukkit-MCP\\dist\\cyanbukkit-mcp.exe",
      "args": []
    }
  }
}
```

更多客户端配置见 [`docs/MCP_CLIENT_CONFIG.md`](docs/MCP_CLIENT_CONFIG.md)。

## 从源码一键构建 exe

本项目默认使用 Conda 环境 `mcpmaker` 构建：

```bat
build.bat
```

Git Bash 用户也可以运行：

```bash
./build.sh
```

构建完成后会生成：

```text
dist/cyanbukkit-mcp.exe
```

默认图标来源：

```text
F:\综合图片库\青桐桶\108_16x16.ico
```

如果要指定 PNG 或 ICO：

```bat
build.bat --icon "F:\综合图片库\青桐桶\28.png"
```

PNG 图标转换需要 Pillow：

```bat
conda run -n mcpmaker pip install pillow
```

## 开发模式运行

不想编译 exe 时，可以直接使用 Conda 环境运行源码。

Windows：

```bat
scripts\cyanbukkit-mcp.bat
```

Git Bash：

```bash
./scripts/cyanbukkit-mcp
```

这些脚本固定使用：

```text
C:\ProgramData\miniconda3\envs\mcpmaker\python.exe
```

## 手动安装开发环境

```bash
conda create -n mcpmaker python=3.11
conda run -n mcpmaker pip install -e .[build,dev]
```

手动启动：

```bash
conda run -n mcpmaker python -m cyanbukkit_mcp
```

## 目录说明

```text
CyanBukkit-MCP/
├── src/cyanbukkit_mcp/      # FastMCP 服务源码
├── knowledge/               # JavaDoc、Wiki、插件 API 知识库
├── scripts/                 # 抓取脚本与 Conda 启动脚本
├── docs/                    # 配置说明与项目文档
├── build.py                 # PyInstaller exe 构建脚本
├── build.bat                # Windows 一键构建
├── build.sh                 # Git Bash 一键构建
└── pyproject.toml           # Python 项目配置
```

## 当前 MCP 工具

- `search_javadoc`：搜索 Paper/Bukkit JavaDoc。
- `get_javadoc_class`：获取指定类的完整 JavaDoc。
- `search_wiki`：搜索 SpigotMC Wiki。
- `list_available_artifacts`：列出知识库 artifact。
- `get_artifact_info`：查看 artifact 详情。

## 验证

```bash
conda run -n mcpmaker python -m cyanbukkit_mcp
conda run -n mcpmaker python build.py
pytest
ruff check
```
