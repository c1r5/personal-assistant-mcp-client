from modules.helpers.mcp_tools import load_mcp_tool_from_file

tools = load_mcp_tool_from_file()

print(f"Loaded {len(tools)} tools from MCP.")