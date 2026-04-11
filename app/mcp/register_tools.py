# app/mcp/register_tools.py

from app.mcp.mcp_server import mcp_server
from app.services.semantic_scholar import search_papers
from app.core.logging import get_logger

logger = get_logger("register_tools")


def register_all_tools():
    mcp_server.register_tool(
        name="web_search",
        description="DuckDuckGo se web search karo",
        handler=lambda query, max_results=5: search_papers(query, max_results),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    )

    logger.info("All MCP tools registered", count=len(mcp_server.list_tools()))