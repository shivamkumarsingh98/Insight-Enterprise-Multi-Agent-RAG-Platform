# app/memory/long_term.py

import json
import os
import time
import uuid
from typing import Optional
from app.core.logging import get_logger

logger = get_logger("long_term_memory")

STORAGE_DIR = "data/long_term_memory"


class LongTermMemory:
    """
    File-based long term memory.
    Production mein isko Redis ya PostgreSQL se replace karo.
    """

    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        logger.info("LongTermMemory initialized", storage_dir=STORAGE_DIR)

    def _get_path(self, user_id: str) -> str:
        return os.path.join(STORAGE_DIR, f"{user_id}.json")

    def save(self, user_id: str, key: str, value: dict):
        path = self._get_path(user_id)

        # Load existing
        data = self._load_raw(user_id)

        data[key] = {
            "value": value,
            "saved_at": time.time(),
            "id": str(uuid.uuid4())[:8]
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info("Long term memory saved", user_id=user_id, key=key)

    def get(self, user_id: str, key: str) -> Optional[dict]:
        data = self._load_raw(user_id)
        entry = data.get(key)
        if entry:
            return entry["value"]
        return None

    def get_all(self, user_id: str) -> dict:
        data = self._load_raw(user_id)
        return {k: v["value"] for k, v in data.items()}

    def delete(self, user_id: str, key: str):
        data = self._load_raw(user_id)
        if key in data:
            del data[key]
            path = self._get_path(user_id)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info("Long term memory deleted", user_id=user_id, key=key)

    def save_query_history(self, user_id: str, query: str, result_count: int):
        """User ke past queries save karo"""
        history = self.get(user_id, "query_history") or []
        history.append({
            "query": query,
            "result_count": result_count,
            "timestamp": time.time()
        })
        # Sirf last 50 queries rakhte hain
        history = history[-50:]
        self.save(user_id, "query_history", history)

    def get_query_history(self, user_id: str) -> list:
        return self.get(user_id, "query_history") or []

    def _load_raw(self, user_id: str) -> dict:
        path = self._get_path(user_id)
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to load long term memory", user_id=user_id, error=str(e))
            return {}


# Global singleton
long_term_memory = LongTermMemory()