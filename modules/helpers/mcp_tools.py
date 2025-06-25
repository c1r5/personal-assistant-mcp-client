import json
import os

from mcp import StdioServerParameters

logger = __import__('logging').getLogger(__name__)

def load_mcp_tool_from_file() -> dict:
    tools = {}
    
    try:
        with open(".vscode/mcp.json", "r") as file:
            mcp_tools = json.load(file)["servers"]
            tools_names = mcp_tools.keys()
            
        for tool_name in tools_names:
            tool_data = mcp_tools[tool_name]
            tool_data["transport"] = tool_data.pop("type")
            tools[tool_name] = tool_data
    except FileNotFoundError:
        logger.error("mcp.json file not found. Please ensure it exists in the current directory.")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from mcp.json: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading MCP tools: {e}")
    finally:
        return tools