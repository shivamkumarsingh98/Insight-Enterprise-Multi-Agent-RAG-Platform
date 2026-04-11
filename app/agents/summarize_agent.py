# # app/agents/summarize_agent.py

# # app/agents/summarize_agent.py
# # app/agents/summarize_agent.py

# def summarize_agent(paper: dict):
#     return paper["summary"][:300]

# # def summarize_paper(paper):
# #     summary = paper['summary'][:300]  
# #     return summary

# app/agents/summarize_agent.py

from app.core.llm import call_llm
from app.core.logging import get_logger

logger = get_logger("summarize_agent")

SYSTEM_PROMPT = """You are a research assistant that summarizes academic papers and articles.
Always respond in clear, concise English.
Focus on: main contribution, methodology, key findings.
Keep summary under 150 words."""


def summarize_agent(paper: dict) -> str:
    title = paper.get("title", "Unknown")
    raw_summary = paper.get("summary", "")
    link = paper.get("link", "")

    if not raw_summary:
        return "No content available to summarize."

    prompt = f"""Paper Title: {title}

Content: {raw_summary[:1000]}

Write a clear 3-4 sentence summary covering:
1. What this is about
2. Key findings or approach
3. Why it matters"""

    try:
        summary = call_llm(prompt, system=SYSTEM_PROMPT, max_tokens=200)
        logger.info("Paper summarized", title=title[:50])
        return summary

    except Exception as e:
        logger.error("Summarization failed", error=str(e), title=title[:50])
        # Fallback — LLM fail ho toh raw text return karo
        return raw_summary[:300]