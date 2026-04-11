# app/mcp/mcp_server.py

import time
import uuid
from typing import Callable, Any, Optional
from app.core.logging import get_logger

logger = get_logger("mcp_server")


class MCPToolResult:
    def __init__(self, tool_name: str, success: bool,
                 data: Any = None, error: str = "", duration_ms: float = 0):
        self.call_id = str(uuid.uuid4())[:8]
        self.tool_name = tool_name
        self.success = success
        self.data = data
        self.error = error
        self.duration_ms = duration_ms
        self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            "call_id": self.call_id,
            "tool_name": self.tool_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "duration_ms": self.duration_ms
        }


class MCPTool:
    def __init__(self, name: str, description: str,
                 handler: Callable, input_schema: dict):
        self.name = name
        self.description = description
        self.handler = handler
        self.input_schema = input_schema   # JSON Schema format
        self.call_count = 0
        self.error_count = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "call_count": self.call_count,
            "error_count": self.error_count
        }


class MCPServer:
    """
    Model Context Protocol server.
    Agents ko standardized tools milte hain — arxiv, web search, RAG, etc.
    Naya tool add karna = sirf register() call karo.
    """

    def __init__(self):
        self._tools: dict[str, MCPTool] = {}
        logger.info("MCPServer initialized")

    def register_tool(self, name: str, description: str,
                      handler: Callable, input_schema: dict) -> MCPTool:
        tool = MCPTool(name, description, handler, input_schema)
        self._tools[name] = tool
        logger.info("MCP tool registered", tool_name=name)
        return tool

    def call(self, tool_name: str, **kwargs) -> MCPToolResult:
        tool = self._tools.get(tool_name)
        if not tool:
            logger.error("MCP tool not found", tool_name=tool_name)
            return MCPToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool '{tool_name}' not registered"
            )

        start = time.time()
        try:
            result = tool.handler(**kwargs)
            duration_ms = round((time.time() - start) * 1000, 2)
            tool.call_count += 1

            logger.info("MCP tool called",
                tool_name=tool_name,
                duration_ms=duration_ms
            )
            return MCPToolResult(
                tool_name=tool_name,
                success=True,
                data=result,
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = round((time.time() - start) * 1000, 2)
            tool.call_count += 1
            tool.error_count += 1
            logger.error("MCP tool failed",
                tool_name=tool_name,
                error=str(e)
            )
            return MCPToolResult(
                tool_name=tool_name,
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )

    def list_tools(self) -> list[dict]:
        return [t.to_dict() for t in self._tools.values()]

    def get_tool(self, name: str) -> Optional[MCPTool]:
        return self._tools.get(name)


# Global singleton
mcp_server = MCPServer()