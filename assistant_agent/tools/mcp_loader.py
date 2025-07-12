import logging
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseConnectionParams,
    StreamableHTTPConnectionParams,
    StdioConnectionParams,
)
from mcp import StdioServerParameters
from typing import Any, Dict, Literal


logger = logging.getLogger(__name__)

Transport = Literal["stdio", "sse", "streamable_http"]
MCPServerConfig = dict[str, dict[str, str]]
Connection = Dict[str, Any]
DiscoveredServers = Dict[str, Connection]


def _mcp_config_server_parser(mcp_server_configs: MCPServerConfig) -> DiscoveredServers:
    discovered_servers: DiscoveredServers = {}

    for server_name in mcp_server_configs.keys():
        server_config = mcp_server_configs[server_name]

        server_config.pop("type", "<none>")

        discovered_servers[server_name] = {**server_config}

        stdio_required_params = ["command", "args"]

        if all(
            [(required in server_config.keys()) for required in stdio_required_params]
        ):
            discovered_servers[server_name]["transport"] = "stdio"

        elif "url" in server_config:
            url = server_config["url"]
            if "/mcp" in url:
                discovered_servers[server_name]["transport"] = "streamable_http"
            elif "/sse":
                discovered_servers[server_name]["transport"] = "sse"
        else:
            raise ValueError(
                "Does not able to determine server type, should be: SSE, HTTP or STDIO"
            )

    return discovered_servers


def _load_mcp_toolset(connection: Connection) -> MCPToolset:
    transport_type: Transport = connection["transport"]

    match transport_type:
        case "stdio":
            return MCPToolset(
                connection_params=StdioConnectionParams(
                    timeout=60,
                    server_params=StdioServerParameters(
                        command=connection["command"],
                        args=connection["args"],
                        env=connection.get("env", {}),
                    ),
                )
            )
        case "sse":
            return MCPToolset(
                connection_params=SseConnectionParams(
                    url=connection["url"],
                    headers=connection.get("headers", {}),
                    timeout=60,
                )
            )
        case "streamable_http":
            return MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=connection["url"],
                    headers=connection.get("headers", {}),
                    timeout=60,
                )
            )


def load_mcp_servers(mcp_config: MCPServerConfig) -> list[MCPToolset]:
    servers = _mcp_config_server_parser(mcp_config)
    toolset = [_load_mcp_toolset(connection) for _, connection in servers.items()]

    logger.info(f"Discovered and Loaded {len(toolset)} tools")

    return toolset
