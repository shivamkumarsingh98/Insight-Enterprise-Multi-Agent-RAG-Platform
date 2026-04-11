# app/agents/rerank_agent.py

from app.core.logging import get_logger

logger = get_logger("rerank_agent")

QUALITY_SOURCES = [
    "arxiv.org", "nature.com", "science.org", "pubmed",
    "ieee.org", "acm.org", "springer.com", "wiley.com",
    "scholar.google", "researchgate.net", "ncbi.nlm.nih.gov",
    "jstor.org", "eric.ed.gov", "ssrn.com"
]

POOR_SOURCES = [
    "quora.com", "reddit.com", "yahoo.com",
    "pinterest.com", "facebook.com", "twitter.com"
]


def _score_result(result: dict, query: str) -> float:
    query_words = set(query.lower().split())
    score = 0.0

    # Source quality score (0-40 points)
    link = result.get("link", "").lower()
    source = result.get("source", "").lower()

    if source == "arxiv":
        score += 40
    else:
        for qs in QUALITY_SOURCES:
            if qs in link:
                score += 35
                break
        for ps in POOR_SOURCES:
            if ps in link:
                score -= 20
                break

    # Relevance score (0-30 points)
    title = result.get("title", "").lower()
    summary = result.get("summary", "").lower()
    text = title + " " + summary

    matched = sum(1 for w in query_words if w in text and len(w) > 3)
    relevance = min(matched / max(len(query_words), 1), 1.0)
    score += relevance * 30

    # Content quality (0-20 points)
    summary_len = len(result.get("summary", ""))
    if summary_len > 500:
        score += 20
    elif summary_len > 200:
        score += 10
    elif summary_len > 50:
        score += 5

    # Has authors = academic (0-10 points)
    if result.get("authors"):
        score += 10

    return round(score, 2)


def rerank_agent(results: list, query: str, top_k: int = 5) -> list:
    """
    Results ko quality + relevance ke hisaab se rank karo.
    Best results upar aate hain.
    """
    if not results:
        return []

    scored = []
    for r in results:
        score = _score_result(r, query)
        scored.append({**r, "_score": score})

    scored.sort(key=lambda x: x["_score"], reverse=True)
    top_results = scored[:top_k]

    logger.info("Results reranked",
        total=len(results),
        returned=len(top_results),
        top_score=top_results[0]["_score"] if top_results else 0
    )

    return top_results