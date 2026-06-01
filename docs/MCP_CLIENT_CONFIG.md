# MCP 客户端配置

`cyanbukkit-mcp.exe` 是 stdio MCP 服务。配置时只需要把 `command` 指向 exe 的绝对路径，通常不需要 `args`。

请把下面示例里的路径替换成你自己的 exe 路径：

```text
G:\Ai_Agent\CyanBukkit-MCP\dist\cyanbukkit-mcp.exe
```

## Claude Desktop

配置文件通常在：

```text
%APPDATA%\Claude\claude_desktop_config.json
```

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

## Claude Code / 通用 stdio MCP

```json
{
  "mcpServers": {
    "cyanbukkit": {
      "command": "G:\\Ai_Agent\\CyanBukkit-MCP\\dist\\cyanbukkit-mcp.exe",
      "args": [],
      "transport": "stdio"
    }
  }
}
```

## Cline / Roo Code

不同版本的配置字段可能略有差异。如果你的客户端使用数组格式，可以参考：

```json
{
  "mcpServers": [
    {
      "name": "cyanbukkit",
      "command": "G:\\Ai_Agent\\CyanBukkit-MCP\\dist\\cyanbukkit-mcp.exe",
      "args": [],
      "transportType": "stdio"
    }
  ]
}
```

如果你的客户端使用对象格式，可以参考：

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

## 开发模式：不编译 exe

Windows：

```json
{
  "mcpServers": {
    "cyanbukkit-dev": {
      "command": "G:\\Ai_Agent\\CyanBukkit-MCP\\scripts\\cyanbukkit-mcp.bat",
      "args": []
    }
  }
}
```

Git Bash 脚本只建议在支持 bash 的 MCP 客户端中使用：

```json
{
  "mcpServers": {
    "cyanbukkit-dev": {
      "command": "G:\\Ai_Agent\\CyanBukkit-MCP\\scripts\\cyanbukkit-mcp",
      "args": []
    }
  }
}
```

## 注意事项

- Windows 路径在 JSON 中要写成双反斜杠：`\\`。
- 推荐使用绝对路径。
- stdio 服务启动后会等待客户端发送 MCP JSON-RPC 消息，直接双击 exe 看起来可能“没有界面”，这是正常的。
- 如果使用源码脚本，必须先准备 Conda 环境 `mcpmaker`。
