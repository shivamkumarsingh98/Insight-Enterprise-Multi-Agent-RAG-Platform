# app/agents/citation_agent.py

import re
from app.core.logging import get_logger

logger = get_logger("citation_agent")


def _format_apa(result: dict, index: int) -> str:
    """APA format citation banao"""
    authors = result.get("authors", [])
    title = result.get("title", "Unknown Title")
    published = result.get("published", "n.d.")
    link = result.get("link", "")
    source = result.get("source", "web")

    year = published[:4] if published and len(published) >= 4 else "n.d."

    if authors:
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) <= 3:
            author_str = ", ".join(authors[:-1]) + f", & {authors[-1]}"
        else:
            author_str = f"{authors[0]} et al."
    else:
        author_str = "Unknown Author"

    if source == "arxiv":
        citation = f"[{index}] {author_str} ({year}). *{title}*. arXiv. {link}"
    else:
        citation = f"[{index}] {author_str} ({year}). {title}. Retrieved from {link}"

    return citation


def citation_agent(results: list) -> dict:
    """
    Results ke liye proper academic citations banao.
    APA format mein.
    """
    if not results:
        return {"citations": [], "formatted": "No sources to cite."}

    citations = []
    for i, result in enumerate(results, 1):
        citation = _format_apa(result, i)
        citations.append({
            "index": i,
            "citation": citation,
            "title": result.get("title", ""),
            "link": result.get("link", "")
        })

    # Formatted bibliography
    formatted = "\n\n".join([c["citation"] for c in citations])
    formatted = "## References\n\n" + formatted

    logger.info("Citations generated", count=len(citations))

    return {
        "citations": citations,
        "formatted": formatted,
        "count": len(citations)
    }