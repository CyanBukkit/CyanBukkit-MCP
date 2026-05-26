# CyanBukkit-MCP

CyanBukkit-MCP 是面向 Minecraft Java 服务端生态的 MCP（Model Context Protocol）服务项目，目标是让 AI Agent 能够结构化访问 Bukkit/Spigot/Paper 插件开发资料与常用生态能力，降低开服插件开发门槛。

项目计划基于 FastMCP 构建，围绕 NMS、ProtocolLib、PlaceholderAPI、Vault 以及全版本 SpigotMC JavaDoc 提供统一的检索、问答、代码辅助与版本差异分析能力。

## 初始目标

- 接入全版本 SpigotMC JavaDoc，并支持按版本、包名、类名、方法名检索。
- 建立 NMS 版本映射与差异知识库，辅助跨版本插件开发。
- 接入 ProtocolLib、PlaceholderAPI、Vault 等主流插件 API 文档。
- 为 AI Agent 暴露标准 MCP tools/resources/prompts。
- 支持后续文档统一归类、索引构建与自动更新。

## 目录规划

```text
CyanBukkit-MCP/
├── docs/                 # 策划案、设计文档、文档归类说明
├── src/                  # FastMCP 服务端源码
├── knowledge/            # 原始/整理后的 JavaDoc 与生态文档索引
├── scripts/              # 文档抓取、清洗、索引生成脚本
├── tests/                # MCP 工具与索引测试
└── pyproject.toml        # Python 项目配置
```

## 当前状态

本仓库处于项目初始化阶段，先建立策划与架构方向。后续可按模块逐步实现 MCP 服务、文档索引器与生态适配器。
