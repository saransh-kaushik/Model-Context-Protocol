from pydantic_ai import RunContext, Tool as PydanticTool
from pydantic_ai.tools import ToolDefinition
from mcp.types import Tool as MCPTool
from mcp import ClientSession
from typing import Any, List
import json

async def mcp_tools(session: ClientSession) -> List[PydanticTool]:
    """Convert MCP tools to pydantic_ai Tools."""
    await session.initialize()
    tools = (await session.list_tools()).tools
    return [create_tool_instance(session, tool) for tool in tools]

def create_tool_instance(session: ClientSession, tool: MCPTool) -> PydanticTool:
    """Initialize a Pydantic AI Tool from an MCP Tool."""
    async def execute_tool(**kwargs: Any) -> Any:
        return await session.call_tool(tool.name, arguments=kwargs)

    async def prepare_tool(ctx: RunContext, tool_def: ToolDefinition) -> ToolDefinition | None:
        # Get the input schema and convert to dict if it's a string
        input_schema = tool.inputSchema
        if isinstance(input_schema, str):
            input_schema = json.loads(input_schema)
        
        # Remove $schema field if present
        if isinstance(input_schema, dict) and "$schema" in input_schema:
            input_schema.pop("$schema")
        
        # If properties exist and have $schema fields, remove them
        if isinstance(input_schema, dict) and "properties" in input_schema:
            for prop in input_schema["properties"].values():
                if isinstance(prop, dict) and "$schema" in prop:
                    prop.pop("$schema")
        
        # Assign the cleaned schema
        tool_def.parameters_json_schema = input_schema
        return tool_def
    
    return PydanticTool(
        execute_tool,
        name=tool.name,
        description=tool.description or "",
        takes_ctx=False,
        prepare=prepare_tool
    )