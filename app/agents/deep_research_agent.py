# app/agents/deep_research_agent.py

import time
from app.core.llm import call_llm
from app.core.logging import get_logger
from app.agents.arxiv_agent import arxiv_agent
from app.agents.search_agent import search_agent

logger = get_logger("deep_research_agent")

def _generate_subqueries(query: str) -> list[str]:
    """Main query se 3-4 sub-queries banao LLM se"""
    prompt = f"""You are a research expert. Given a research topic, generate 4 specific sub-queries to comprehensively research it.

Topic: {query}

Generate exactly 4 sub-queries. Return ONLY the queries, one per line, no numbering, no extra text."""

    try:
        response = call_llm(prompt, max_tokens=200)
        subqueries = [q.strip() for q in response.strip().split("\n") if q.strip()]
        subqueries = subqueries[:4]
        logger.info("Sub-queries generated", count=len(subqueries), original=query)
        return subqueries
    except Exception as e:
        logger.error("Sub-query generation failed", error=str(e))
        return [query]


def _synthesize_report(query: str, all_results: list) -> str:
    """Sab results ko ek comprehensive report mein combine karo"""

    context_parts = []
    for r in all_results[:8]:
        context_parts.append(
            f"Title: {r.get('title', '')}\n"
            f"Source: {r.get('source', 'web')}\n"
            f"Authors: {', '.join(r.get('authors', []))}\n"
            f"Content: {r.get('summary', '')[:500]}"
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""You are an expert research analyst. Based on the following research materials, write a comprehensive research report.

Topic: {query}

Research Materials:
{context}

Write a detailed report covering:
1. Overview of the topic
2. Key findings and developments
3. Important methodologies or approaches
4. Current state and future directions
5. Key sources and authors

Write in clear academic English. Be specific and cite sources where possible."""

    try:
        report = call_llm(prompt, max_tokens=1000)
        return report
    except Exception as e:
        logger.error("Report synthesis failed", error=str(e))
        return "Report generation failed."


def deep_research_agent(query: str) -> dict:
    """
    Multi-source deep research:
    1. Sub-queries generate karo
    2. Arxiv + Web dono se search karo
    3. Sab combine karke comprehensive report banao
    """
    start_time = time.time()
    logger.info("Deep research started", query=query)

    # Step 1: Sub-queries
    subqueries = _generate_subqueries(query)
    logger.info("Researching sub-queries", subqueries=subqueries)

    # Step 2: Parallel search — arxiv + web
    all_results = []
    seen_titles = set()

    for subq in subqueries:
        # Arxiv se academic papers
        arxiv_results = arxiv_agent(subq, max_results=3)
        for r in arxiv_results:
            if r["title"] not in seen_titles:
                seen_titles.add(r["title"])
                all_results.append(r)

        # Web se bhi
        web_results = search_agent(subq, max_results=2)
        for r in web_results:
            if r["title"] not in seen_titles:
                seen_titles.add(r["title"])
                all_results.append(r)

        time.sleep(0.5)  # Rate limiting

    logger.info("All sources collected", total_results=len(all_results))

    # Step 3: Comprehensive report
    report = _synthesize_report(query, all_results)

    duration = round((time.time() - start_time) * 1000, 2)
    logger.info("Deep research completed", duration_ms=duration, sources=len(all_results))

    return {
        "query": query,
        "subqueries": subqueries,
        "report": report,
        "sources": all_results,
        "total_sources": len(all_results),
        "duration_ms": duration
    }