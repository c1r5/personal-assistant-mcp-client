import json

logger = __import__("logging").getLogger(__name__)


class MCPServerService:
    mcp_servers = {}

    def __init__(self) -> None:
        self.load_mcp_servers()

    def load_mcp_servers(self):
        self.mcp_servers = {}

        try:
            with open(".vscode/mcp.json", "r") as file:
                mcp_tools = json.load(file)["servers"]
                tools_names = mcp_tools.keys()

            for tool_name in tools_names:
                tool_data: dict[str, str] = mcp_tools[tool_name]
                tool_data["transport"] = (
                    "streamable_http"
                    if tool_data["type"] == "http"
                    else tool_data.pop("type")
                )
                tool_data.pop("type", "<default>")
                self.mcp_servers[tool_name] = tool_data
        except FileNotFoundError:
            logger.error(
                "mcp.json file not found. Please ensure it exists in the current directory."
            )
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from mcp.json: {e}")
        except Exception as e:
            logger.exception(e)

