# FastMCP 文档索引摘录

本文件记录 CyanBukkit-MCP 首期实现最相关的 FastMCP 文档入口。完整索引来自 `https://gofastmcp.com/llms.txt`。

## 服务端核心

- The FastMCP Server: https://gofastmcp.com/servers/server.md
- Tools: https://gofastmcp.com/servers/tools.md
- Resources & Templates: https://gofastmcp.com/servers/resources.md
- Prompts: https://gofastmcp.com/servers/prompts.md
- MCP Context: https://gofastmcp.com/servers/context.md
- Testing your FastMCP Server: https://gofastmcp.com/servers/testing.md

## 运行与配置

- Installation: https://gofastmcp.com/getting-started/installation.md
- Quickstart: https://gofastmcp.com/getting-started/quickstart.md
- Running Your Server: https://gofastmcp.com/deployment/running-server.md
- Project Configuration: https://gofastmcp.com/deployment/server-configuration.md
- Running Servers CLI: https://gofastmcp.com/cli/running.md
- Inspecting Servers: https://gofastmcp.com/cli/inspecting.md

## 客户端与集成

- The FastMCP Client: https://gofastmcp.com/clients/client.md
- Calling Tools: https://gofastmcp.com/clients/tools.md
- Reading Resources: https://gofastmcp.com/clients/resources.md
- Getting Prompts: https://gofastmcp.com/clients/prompts.md
- Claude Code Integration: https://gofastmcp.com/integrations/claude-code.md
- MCP JSON Configuration: https://gofastmcp.com/integrations/mcp-json-configuration.md

## 大型知识库相关能力

- Pagination: https://gofastmcp.com/servers/pagination.md
- Background Tasks: https://gofastmcp.com/servers/tasks.md
- Progress Reporting: https://gofastmcp.com/servers/progress.md
- Tool Search: https://gofastmcp.com/servers/transforms/tool-search.md
- Resources as Tools: https://gofastmcp.com/servers/transforms/resources-as-tools.md
- Versioning: https://gofastmcp.com/servers/versioning.md
- Component Visibility: https://gofastmcp.com/servers/visibility.md

## 后续可选能力

- HTTP Deployment: https://gofastmcp.com/deployment/http.md
- Authentication: https://gofastmcp.com/servers/auth/authentication.md
- Authorization: https://gofastmcp.com/servers/authorization.md
- Middleware: https://gofastmcp.com/servers/middleware.md
- OpenTelemetry: https://gofastmcp.com/servers/telemetry.md
- FastAPI Integration: https://gofastmcp.com/integrations/fastapi.md

## CyanBukkit-MCP 实现优先级

1. 先实现本地 stdio MCP 服务：`FastMCP("CyanBukkit-MCP")` + tools/resources/prompts。
2. 首期只做本地文档索引，不做远程 HTTP 部署和认证。
3. 文档量变大后再引入分页、后台任务、进度上报和工具搜索。
4. 对 Claude Code 接入时优先参考 Claude Code Integration 和 MCP JSON Configuration。
