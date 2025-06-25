import json
import os

from mcp import StdioServerParameters
from modules.models import SSEServerParameters

logger = __import__('logging').getLogger(__name__)

def load_mcp_tool_from_file() -> list[SSEServerParameters | StdioServerParameters]:
    try:
        with open(".vscode/mcp.json", "r") as file:
            mcp_tools = json.load(file)["servers"]
            tools_names = mcp_tools.keys()
            tools = []
            for tool_name in tools_names:
                tool_data = mcp_tools[tool_name]
                tool_type = tool_data.get("type", "stdio")
                environment = tool_data.get("env", {})
                
                for key, value in environment.items():
                    os.environ[key] = value 
                        
                match tool_type:
                    case "stdio":
                        tools.append(StdioServerParameters(
                            command=tool_data["command"],
                            args=tool_data.get("args", []),
                        ))
                    case "sse":
                        tools.append(SSEServerParameters(
                            url=tool_data["url"],
                            headers=tool_data.get("headers"),
                        ))
                    case _:
                        raise ValueError(f"Unsupported tool type: {tool_type}")

                logger.info(f"Loaded tool: {tool_name}")

        return tools
    except FileNotFoundError:
        logger.error("mcp.json file not found. Please ensure it exists in the current directory.")
        return []
    
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from mcp.json: {e}")
        return []
    
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading MCP tools: {e}")
        return []