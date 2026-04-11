# app/agents/arxiv_agent.py

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger("arxiv_agent")

ARXIV_API = "http://export.arxiv.org/api/query"

def arxiv_agent(query: str, max_results: int = 5) -> list:
    """
    Real arxiv.org se academic papers fetch karo.
    Free API — no key needed.
    """
    try:
        params = urllib.parse.urlencode({
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        })

        url = f"{ARXIV_API}?{params}"
        logger.info("Arxiv search started", query=query)

        req = urllib.request.Request(url, headers={"User-Agent": "ResearchBot/1.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read().decode("utf-8")

        results = _parse_arxiv_xml(xml_data)
        logger.info("Arxiv search completed", query=query, count=len(results))
        return results

    except Exception as e:
        logger.error("Arxiv search failed", error=str(e), query=query)
        return []


def _parse_arxiv_xml(xml_data: str) -> list:
    """Arxiv XML response parse karo"""
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom"
    }

    root = ET.fromstring(xml_data)
    results = []

    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns)
        summary = entry.find("atom:summary", ns)
        published = entry.find("atom:published", ns)
        link = entry.find("atom:id", ns)

        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.find("atom:name", ns)
            if name is not None:
                authors.append(name.text.strip())

        # Categories
        categories = []
        for cat in entry.findall("atom:category", ns):
            term = cat.get("term", "")
            if term:
                categories.append(term)

        results.append({
            "title": title.text.strip().replace("\n", " ") if title is not None else "No title",
            "authors": authors[:5],
            "summary": summary.text.strip().replace("\n", " ") if summary is not None else "",
            "published": published.text[:10] if published is not None else "",
            "link": link.text.strip() if link is not None else "",
            "source": "arxiv",
            "categories": categories[:3]
        })

    return results