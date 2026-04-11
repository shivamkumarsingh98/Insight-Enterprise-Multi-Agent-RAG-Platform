# app/agents/classifier_agent.py

import re
from enum import Enum
from app.core.logging import get_logger

logger = get_logger("classifier_agent")


class QueryIntent(str, Enum):
    RESEARCH_SEARCH   = "research_search"    # arxiv/papers dhundhna
    RAG_QUESTION      = "rag_question"       # existing knowledge se answer
    SUMMARIZE_ONLY    = "summarize_only"     # koi text summarize karna
    COMPARE           = "compare"            # do cheezein compare karna
    UNKNOWN           = "unknown"


class ClassificationResult:
    def __init__(self, intent: QueryIntent, confidence: float, reasoning: str):
        self.intent = intent
        self.confidence = confidence
        self.reasoning = reasoning

    def to_dict(self):
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }


class ClassifierAgent:
    """
    Rule-based + keyword NLU classifier.
    SLM/LLM routing future mein add hoga.
    Abhi: fast rule-based classification.
    """

    RESEARCH_KEYWORDS = [
        "paper", "papers", "research", "arxiv", "study", "studies",
        "find", "search", "latest", "recent", "published", "journal",
        "publication", "author", "cite", "literature"
    ]
    RAG_KEYWORDS = [
        "what is", "explain", "how does", "tell me about", "define",
        "what are", "describe", "meaning of", "difference between"
    ]
    SUMMARIZE_KEYWORDS = [
        "summarize", "summary", "tldr", "brief", "shorten", "condense",
        "key points", "main points", "overview"
    ]
    COMPARE_KEYWORDS = [
        "compare", "vs", "versus", "difference", "better", "worse",
        "pros and cons", "contrast", "which is"
    ]

    def classify(self, query: str) -> ClassificationResult:
        q = query.lower().strip()
        scores = {
            QueryIntent.RESEARCH_SEARCH: self._score(q, self.RESEARCH_KEYWORDS),
            QueryIntent.RAG_QUESTION:    self._score(q, self.RAG_KEYWORDS),
            QueryIntent.SUMMARIZE_ONLY:  self._score(q, self.SUMMARIZE_KEYWORDS),
            QueryIntent.COMPARE:         self._score(q, self.COMPARE_KEYWORDS),
        }

        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        if best_score == 0:
            result = ClassificationResult(
                QueryIntent.RAG_QUESTION, 0.5,
                "No clear keywords — defaulting to RAG"
            )
        else:
            total = sum(scores.values()) or 1
            confidence = round(best_score / total, 3)
            result = ClassificationResult(
                best_intent, confidence,
                f"Matched keywords for {best_intent.value}"
            )

        logger.info("Query classified",
            query=query[:50],
            intent=result.intent.value,
            confidence=result.confidence
        )
        return result

    def _score(self, text: str, keywords: list) -> int:
        return sum(1 for kw in keywords if kw in text)


# Global singleton
classifier = ClassifierAgent()