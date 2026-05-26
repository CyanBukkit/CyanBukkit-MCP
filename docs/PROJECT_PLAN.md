# CyanBukkit-MCP 策划案

## 1. 项目定位

CyanBukkit-MCP 是一个面向 Minecraft Java 服务端插件开发的 MCP 服务。它把分散在 NMS、SpigotMC JavaDoc、ProtocolLib、PlaceholderAPI、Vault 等生态中的知识转化为可被 AI Agent 调用的结构化能力，让 Agent 能够直接查询 API、理解版本差异、生成插件代码骨架、解释报错并给出迁移建议。

项目基于 FastMCP 构建。FastMCP 的核心模式是用 Python 函数声明 MCP tool/resource/prompt，并自动生成 schema、校验与协议层能力。

## 2. 愿景

打破开服开发插件的壁垒：

- 让服主、插件开发者、整合包作者可以通过自然语言完成常见插件开发任务。
- 让 AI Agent 不再依赖模糊记忆，而是直接访问版本化 JavaDoc 与主流插件 API 文档。
- 让 NMS 跨版本差异、混淆名、包路径变更、事件/API 变化可以被系统化检索。
- 形成 CyanBukkit 生态下可持续更新的 Java 服务端知识 MCP。

## 3. 首期接入范围

### 3.1 SpigotMC JavaDoc 全版本

目标：归档并索引多个 SpigotMC/Bukkit API 版本的 JavaDoc。

能力：

- 按版本检索 class/interface/enum/annotation。
- 按方法名、字段名、包名检索。
- 对比两个版本中的 API 变更。
- 提供 JavaDoc 原文片段、签名、继承关系、弃用标记。

### 3.2 NMS

目标：建立 NMS 版本差异知识层。

能力：

- 查询特定 Minecraft/Spigot 版本的 NMS 包路径。
- 记录常见类、方法、字段在不同版本中的变化。
- 辅助生成 reflection/adapter 代码建议。
- 给出跨版本兼容风险提示。

### 3.3 ProtocolLib

目标：接入 ProtocolLib 文档与常见 Packet 用法。

能力：

- 查询 PacketType、监听器、StructureModifier 用法。
- 生成 packet listener 骨架。
- 解释协议层报错与版本兼容问题。

### 3.4 PlaceholderAPI

目标：接入 PlaceholderAPI 扩展开发资料。

能力：

- 生成 PlaceholderExpansion 骨架。
- 查询占位符注册、解析、刷新策略。
- 给出与 Bukkit 插件生命周期结合的建议。

### 3.5 Vault

目标：接入 Vault Economy/Permission/Chat API。

能力：

- 查询 Economy、Permission、Chat 服务接口。
- 生成服务获取与依赖检测代码。
- 解释软依赖、服务注册、插件兼容逻辑。

## 4. MCP 能力设计

### 4.1 Tools

计划暴露的首批 tools：

- `search_spigot_javadoc(query, version=None, kind=None)`：检索 Spigot/Bukkit JavaDoc。
- `get_javadoc_symbol(symbol, version)`：获取类、方法、字段详情。
- `compare_spigot_versions(symbol, from_version, to_version)`：比较 API 跨版本变化。
- `search_nms_mapping(query, mc_version)`：检索 NMS 类/方法/字段映射与备注。
- `explain_nms_compat(symbol, versions)`：解释 NMS 兼容风险。
- `search_plugin_api(plugin, query, version=None)`：检索 ProtocolLib/PlaceholderAPI/Vault 文档。
- `generate_plugin_skeleton(name, api_version, dependencies)`：生成 Bukkit 插件基础骨架说明。
- `suggest_dependency_setup(dependencies, build_tool)`：生成 Maven/Gradle 依赖配置建议。

### 4.2 Resources

计划暴露的 resources：

- `cyanbukkit://javadocs/versions`：已索引 JavaDoc 版本列表。
- `cyanbukkit://javadocs/{version}/{symbol}`：特定版本符号详情。
- `cyanbukkit://nms/{mc_version}/index`：NMS 版本索引。
- `cyanbukkit://plugins/{plugin}/index`：外部插件 API 索引。
- `cyanbukkit://docs/project-plan`：项目策划案。

### 4.3 Prompts

计划暴露的 prompts：

- `design_bukkit_plugin`：根据需求设计插件架构。
- `migrate_plugin_version`：分析插件从一个服务端版本迁移到另一个版本的风险。
- `debug_bukkit_error`：根据报错栈、依赖、服务端版本定位问题。
- `write_protocol_listener`：生成 ProtocolLib packet 监听逻辑。
- `write_placeholder_expansion`：生成 PlaceholderAPI 扩展逻辑。

## 5. 数据与索引架构

### 5.1 原始数据层

`knowledge/raw/` 保存原始下载或人工归档的文档：

- SpigotMC/Bukkit JavaDoc HTML。
- ProtocolLib 文档、Wiki、JavaDoc。
- PlaceholderAPI 文档、JavaDoc。
- Vault 文档、JavaDoc。
- NMS 版本备注与映射资料。

### 5.2 规范化层

`knowledge/normalized/` 保存清洗后的结构化 JSON/Markdown：

- symbol name
- package
- kind
- version
- signature
- description
- deprecation
- source_url
- relationships

### 5.3 索引层

`knowledge/index/` 保存面向检索的索引：

- 全文搜索索引。
- 符号倒排索引。
- 版本差异索引。
- 插件生态分类索引。

首期可以先用本地 JSON + 简单关键字检索，后续再接入 SQLite FTS、Whoosh、tantivy 或向量索引。

## 6. 项目结构

```text
CyanBukkit-MCP/
├── README.md
├── pyproject.toml
├── docs/
│   └── PROJECT_PLAN.md
├── src/
│   └── cyanbukkit_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── tools/
│       ├── resources/
│       ├── prompts/
│       ├── index/
│       └── adapters/
├── knowledge/
│   ├── raw/
│   ├── normalized/
│   └── index/
├── scripts/
│   ├── fetch_javadocs.py
│   ├── normalize_javadocs.py
│   └── build_index.py
└── tests/
```

## 7. 实施阶段

### Phase 0：项目初始化

- 建立仓库结构。
- 编写策划案与 README。
- 建立 FastMCP 最小服务入口。
- 预留 tools/resources/prompts 模块。

### Phase 1：文档归类与静态检索

- 确定 SpigotMC JavaDoc 版本列表。
- 手动或脚本导入首批文档。
- 建立本地 JSON 文档格式。
- 实现 `search_spigot_javadoc`、`get_javadoc_symbol`。

### Phase 2：生态插件接入

- 接入 ProtocolLib、PlaceholderAPI、Vault 文档。
- 实现统一 `search_plugin_api`。
- 增加插件代码骨架 prompts。

### Phase 3：NMS 版本差异

- 建立常用 NMS 类/方法映射。
- 实现版本差异查询和兼容风险解释。
- 沉淀 reflection/adapter 设计模板。

### Phase 4：Agent 工作流强化

- 增加调试、迁移、架构设计 prompts。
- 增加测试数据与回归用例。
- 评估向量索引和外部搜索后端。

## 8. FastMCP 初始服务形态

最小服务入口示例：

```python
from fastmcp import FastMCP

mcp = FastMCP("CyanBukkit-MCP")

@mcp.tool
def search_spigot_javadoc(query: str, version: str | None = None) -> list[dict]:
    """Search indexed SpigotMC JavaDoc symbols."""
    return []

if __name__ == "__main__":
    mcp.run()
```

实际实现时会把 tools/resources/prompts 拆分到独立模块，并由 `server.py` 统一注册。

## 9. 风险与约束

- JavaDoc 全版本体量大，需要分阶段接入，避免一次性维护成本过高。
- NMS 存在混淆、重映射、服务端分支差异，需要明确数据来源和可信度。
- ProtocolLib 等项目版本与 Minecraft 版本并非一一对应，需要建立兼容矩阵。
- 生成代码必须标注目标服务端版本、Java 版本、构建工具和依赖版本。
- MCP tool 返回内容需要控制长度，避免一次返回过大文档。

## 10. 成功标准

首个可用版本应满足：

- AI Agent 能查询至少一个 SpigotMC JavaDoc 版本的类和方法。
- AI Agent 能查询 ProtocolLib/PlaceholderAPI/Vault 的基础用法。
- AI Agent 能根据需求生成带依赖说明的 Bukkit 插件骨架。
- MCP 服务可本地运行，并可被 Claude Code 或其他 MCP Client 调用。
- 文档归类规则清晰，后续可以持续扩展版本和生态插件。
