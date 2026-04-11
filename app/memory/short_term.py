# app/memory/short_term.py

import uuid
import time
from typing import Optional
from collections import defaultdict
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("short_term_memory")


class Message:
    def __init__(self, role: str, content: str, metadata: dict = {}):
        self.id = str(uuid.uuid4())[:8]
        self.role = role        # "user" | "assistant" | "agent"
        self.content = content
        self.metadata = metadata
        self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: list[Message] = []
        self.created_at = time.time()
        self.last_active = time.time()
        self.metadata = {}

    def add_message(self, role: str, content: str, metadata: dict = {}):
        msg = Message(role, content, metadata)
        self.messages.append(msg)
        self.last_active = time.time()

        # Max history limit — purane messages hatao
        if len(self.messages) > settings.MAX_HISTORY_LENGTH:
            self.messages = self.messages[-settings.MAX_HISTORY_LENGTH:]

        logger.info("Message added", session_id=self.session_id, role=role)
        return msg

    def get_history(self) -> list[dict]:
        return [m.to_dict() for m in self.messages]

    def get_last_n(self, n: int = 5) -> list[dict]:
        return [m.to_dict() for m in self.messages[-n:]]

    def is_expired(self) -> bool:
        return (time.time() - self.last_active) > settings.SESSION_TTL_SECONDS

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "created_at": self.created_at,
            "last_active": self.last_active,
            "metadata": self.metadata
        }


class ShortTermMemory:
    """In-memory session store — process restart pe clear ho jata hai"""

    def __init__(self):
        self._sessions: dict[str, Session] = {}
        logger.info("ShortTermMemory initialized")

    def create_session(self, session_id: Optional[str] = None) -> Session:
        sid = session_id or str(uuid.uuid4())[:12]
        session = Session(sid)
        self._sessions[sid] = session
        logger.info("Session created", session_id=sid)
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session and session.is_expired():
            logger.info("Session expired", session_id=session_id)
            self.delete_session(session_id)
            return None
        return session

    def get_or_create(self, session_id: Optional[str] = None) -> Session:
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        return self.create_session(session_id)

    def delete_session(self, session_id: str):
        self._sessions.pop(session_id, None)
        logger.info("Session deleted", session_id=session_id)

    def cleanup_expired(self):
        """Background mein call karo — expired sessions hatao"""
        expired = [
            sid for sid, s in self._sessions.items()
            if s.is_expired()
        ]
        for sid in expired:
            self.delete_session(sid)
        if expired:
            logger.info("Expired sessions cleaned", count=len(expired))

    def get_stats(self) -> dict:
        return {
            "total_sessions": len(self._sessions),
            "active_sessions": sum(
                1 for s in self._sessions.values()
                if not s.is_expired()
            )
        }


# Global singleton — poori app mein ek hi instance
memory = ShortTermMemory()