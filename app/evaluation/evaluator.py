# app/evaluation/evaluator.py

import time
import uuid
import json
import os
import random
from typing import Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("evaluator")

EVAL_DIR = "data/evaluations"


class EvalResult:
    def __init__(self, eval_id: str, query: str, result_count: int,
                 relevance_score: float, quality_score: float,
                 feedback: str, duration_ms: float):
        self.eval_id = eval_id
        self.query = query
        self.result_count = result_count
        self.relevance_score = relevance_score   # 0.0 - 1.0
        self.quality_score = quality_score       # 0.0 - 1.0
        self.feedback = feedback
        self.duration_ms = duration_ms
        self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            "eval_id": self.eval_id,
            "query": self.query,
            "result_count": self.result_count,
            "relevance_score": self.relevance_score,
            "quality_score": self.quality_score,
            "feedback": self.feedback,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp
        }


class LLMJudgeEvaluator:
    """
    LLM-as-judge evaluation system.
    Abhi: heuristic scoring (fast, no extra API calls).
    Production mein: async LLM call add karo for deep eval.
    """

    def __init__(self):
        os.makedirs(EVAL_DIR, exist_ok=True)
        self._log_path = os.path.join(EVAL_DIR, "evaluations.jsonl")
        logger.info("LLMJudgeEvaluator initialized")

    def should_evaluate(self) -> bool:
        """Sample rate check — sirf X% requests evaluate karo"""
        return random.random() < settings.EVAL_SAMPLE_RATE

    def evaluate(self, query: str, results: list, duration_ms: float) -> Optional[EvalResult]:
        if not settings.ENABLE_EVALUATION:
            return None
        if not self.should_evaluate():
            return None

        start = time.time()
        eval_id = str(uuid.uuid4())[:8]

        # Heuristic scoring
        relevance_score = self._score_relevance(query, results)
        quality_score = self._score_quality(results)
        feedback = self._generate_feedback(relevance_score, quality_score, results)

        eval_duration = round((time.time() - start) * 1000, 2)

        result = EvalResult(
            eval_id=eval_id,
            query=query,
            result_count=len(results),
            relevance_score=relevance_score,
            quality_score=quality_score,
            feedback=feedback,
            duration_ms=eval_duration
        )

        self._save(result)

        logger.info("Evaluation completed",
            eval_id=eval_id,
            relevance=relevance_score,
            quality=quality_score
        )
        return result

    def _score_relevance(self, query: str, results: list) -> float:
        if not results:
            return 0.0
        query_words = set(query.lower().split())
        scores = []
        for r in results:
            title = r.get("title", "").lower()
            summary = r.get("summary", "").lower()
            text = title + " " + summary
            matched = sum(1 for w in query_words if w in text and len(w) > 3)
            scores.append(min(matched / max(len(query_words), 1), 1.0))
        return round(sum(scores) / len(scores), 3)

    def _score_quality(self, results: list) -> float:
        if not results:
            return 0.0
        scores = []
        for r in results:
            summary = r.get("summary", "")
            title = r.get("title", "")
            link = r.get("link", "")
            score = 0.0
            if len(summary) > 100:  score += 0.4
            if len(summary) > 300:  score += 0.2
            if len(title) > 10:     score += 0.2
            if link.startswith("http"):  score += 0.2
            scores.append(min(score, 1.0))
        return round(sum(scores) / len(scores), 3)

    def _generate_feedback(self, relevance: float, quality: float,
                            results: list) -> str:
        issues = []
        if relevance < 0.3:
            issues.append("Low relevance to query")
        if quality < 0.4:
            issues.append("Poor result quality (short summaries or missing links)")
        if len(results) == 0:
            issues.append("No results returned")
        if len(results) < 3:
            issues.append("Few results — consider expanding search")
        return "; ".join(issues) if issues else "Results look good"

    def _save(self, result: EvalResult):
        try:
            with open(self._log_path, "a") as f:
                f.write(json.dumps(result.to_dict()) + "\n")
        except Exception as e:
            logger.error("Eval save failed", error=str(e))

    def get_stats(self) -> dict:
        if not os.path.exists(self._log_path):
            return {"total_evals": 0}
        try:
            with open(self._log_path, "r") as f:
                lines = [json.loads(l) for l in f if l.strip()]
            if not lines:
                return {"total_evals": 0}
            avg_relevance = sum(e["relevance_score"] for e in lines) / len(lines)
            avg_quality = sum(e["quality_score"] for e in lines) / len(lines)
            return {
                "total_evals": len(lines),
                "avg_relevance_score": round(avg_relevance, 3),
                "avg_quality_score": round(avg_quality, 3),
                "last_eval_at": lines[-1]["timestamp"]
            }
        except Exception as e:
            logger.error("Eval stats failed", error=str(e))
            return {"total_evals": 0, "error": str(e)}


# Global singleton
evaluator = LLMJudgeEvaluator()