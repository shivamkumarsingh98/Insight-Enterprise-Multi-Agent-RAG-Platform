# app/governance/audit.py

import json
import os
import time
import uuid
from typing import Optional
from app.core.logging import get_logger

logger = get_logger("audit")

AUDIT_DIR = "data/audit_logs"


class AuditEvent:
    def __init__(
        self,
        event_type: str,         # "api_call" | "agent_run" | "auth_attempt" | "error"
        user_id: Optional[str],
        session_id: Optional[str],
        action: str,
        details: dict,
        status: str = "success",  # success | failure | blocked
        correlation_id: str = ""
    ):
        self.id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.event_type = event_type
        self.user_id = user_id or "anonymous"
        self.session_id = session_id or ""
        self.action = action
        self.details = details
        self.status = status
        self.correlation_id = correlation_id

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "action": self.action,
            "details": self.details,
            "status": self.status,
            "correlation_id": self.correlation_id
        }


class AuditTrail:
    """
    Append-only audit log.
    Production mein: PostgreSQL ya dedicated audit DB use karo.
    """

    def __init__(self):
        os.makedirs(AUDIT_DIR, exist_ok=True)
        self._log_path = os.path.join(AUDIT_DIR, "audit.jsonl")
        logger.info("AuditTrail initialized", path=self._log_path)

    def log(self, event: AuditEvent):
        try:
            with open(self._log_path, "a") as f:
                f.write(json.dumps(event.to_dict()) + "\n")
            logger.info("Audit event logged",
                event_type=event.event_type,
                action=event.action,
                status=event.status
            )
        except Exception as e:
            logger.error("Audit log write failed", error=str(e))

    def log_api_call(self, user_id: str, session_id: str,
                     endpoint: str, query: str,
                     result_count: int, duration_ms: float,
                     correlation_id: str = ""):
        self.log(AuditEvent(
            event_type="api_call",
            user_id=user_id,
            session_id=session_id,
            action=endpoint,
            details={"query": query, "result_count": result_count,
                     "duration_ms": duration_ms},
            status="success",
            correlation_id=correlation_id
        ))

    def log_auth(self, user_id: str, success: bool, path: str):
        self.log(AuditEvent(
            event_type="auth_attempt",
            user_id=user_id,
            session_id=None,
            action="authenticate",
            details={"path": path},
            status="success" if success else "failure"
        ))

    def get_recent(self, limit: int = 100) -> list[dict]:
        """Last N audit events wapas karo"""
        if not os.path.exists(self._log_path):
            return []
        try:
            with open(self._log_path, "r") as f:
                lines = f.readlines()
            events = [json.loads(l) for l in lines[-limit:] if l.strip()]
            return list(reversed(events))
        except Exception as e:
            logger.error("Audit read failed", error=str(e))
            return []


# Global singleton
audit_trail = AuditTrail()