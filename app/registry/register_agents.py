# app/registry/register_agents.py

from app.registry.agent_registry import registry, AgentCapability
from app.agents.search_agent import search_agent
from app.agents.summarize_agent import summarize_agent
from app.agents.arxiv_agent import arxiv_agent
from app.agents.rerank_agent import rerank_agent
from app.agents.citation_agent import citation_agent
from app.agents.deep_research_agent import deep_research_agent
from app.core.logging import get_logger

logger = get_logger("register_agents")


def register_all_agents():
    """App startup pe call karo"""

    registry.register(
        name="search_agent",
        version="1.0.0",
        capabilities=[AgentCapability.SEARCH],
        handler=search_agent,
        description="DuckDuckGo web search"
    )

    registry.register(
        name="arxiv_agent",
        version="1.0.0",
        capabilities=[AgentCapability.SEARCH],
        handler=arxiv_agent,
        description="Arxiv.org se real academic papers — PhD level research"
    )

    registry.register(
        name="summarize_agent",
        version="1.0.0",
        capabilities=[AgentCapability.SUMMARIZE],
        handler=summarize_agent,
        description="Groq LLaMA se AI summary"
    )

    registry.register(
        name="rerank_agent",
        version="1.0.0",
        capabilities=[AgentCapability.RAG],
        handler=lambda results, query: rerank_agent(results, query),
        description="Results quality filter + relevance ranking"
    )

    registry.register(
        name="citation_agent",
        version="1.0.0",
        capabilities=[AgentCapability.RAG],
        handler=citation_agent,
        description="APA format academic citations"
    )

    registry.register(
        name="deep_research_agent",
        version="1.0.0",
        capabilities=[AgentCapability.RAG],
        handler=lambda query: deep_research_agent(query),
        description="Multi-source deep research — sub-queries + synthesis"
    )

    logger.info("All agents registered", count=len(registry.get_all()))