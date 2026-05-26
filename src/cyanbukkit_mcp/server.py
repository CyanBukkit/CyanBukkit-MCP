from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP("CyanBukkit-MCP")


@mcp.tool
def search_spigot_javadoc(query: str, version: Optional[str] = None, kind: Optional[str] = None) -> list[dict]:
    """Search indexed SpigotMC JavaDoc symbols."""
    return []


@mcp.tool
def search_plugin_api(plugin: str, query: str, version: Optional[str] = None) -> list[dict]:
    """Search indexed ProtocolLib, PlaceholderAPI, or Vault API documentation."""
    return []


@mcp.tool
def search_nms_mapping(query: str, mc_version: str) -> list[dict]:
    """Search indexed NMS mappings and compatibility notes."""
    return []


@mcp.resource("cyanbukkit://docs/project-plan")
def project_plan() -> str:
    """Return the CyanBukkit-MCP project plan location."""
    return "docs/PROJECT_PLAN.md"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
