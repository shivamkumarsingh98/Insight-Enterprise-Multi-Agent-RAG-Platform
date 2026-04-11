# app/core/logging.py

import logging
import json
import uuid
import time
from datetime import datetime
from contextvars import ContextVar
from typing import Optional

# Context variable — har request ka apna correlation_id
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")
session_id_var: ContextVar[str] = ContextVar("session_id", default="")

def generate_correlation_id() -> str:
    return str(uuid.uuid4())[:8]

def set_correlation_id(cid: str):
    correlation_id_var.set(cid)

def get_correlation_id() -> str:
    return correlation_id_var.get() or generate_correlation_id()

def set_session_id(sid: str):
    session_id_var.set(sid)

def get_session_id() -> str:
    return session_id_var.get() or ""


class JSONFormatter(logging.Formatter):
    """Har log line JSON format mein — production ready"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "correlation_id": get_correlation_id(),
            "session_id": get_session_id(),
        }

        # Extra fields agar hain
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class AgentLogger:
    """Har agent ke liye dedicated logger"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name

    def info(self, message: str, **kwargs):
        self.logger.info(message, extra={"extra": {"agent": self.name, **kwargs}})

    def error(self, message: str, **kwargs):
        self.logger.error(message, extra={"extra": {"agent": self.name, **kwargs}})

    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra={"extra": {"agent": self.name, **kwargs}})

    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra={"extra": {"agent": self.name, **kwargs}})

    def log_step(self, step: str, data: dict = {}):
        self.info(f"STEP: {step}", step=step, **data)

    def log_timing(self, operation: str, duration_ms: float):
        self.info(f"TIMING: {operation}", operation=operation, duration_ms=duration_ms)


def setup_logging(level: str = "INFO"):
    """App startup pe ek baar call karo"""

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console handler
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # File handler — production mein zaroori
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> AgentLogger:
    return AgentLogger(name)


class TimingContext:
    """Context manager — kisi bhi operation ka time measure karo"""

    def __init__(self, logger: AgentLogger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        duration_ms = (time.time() - self.start_time) * 1000
        self.logger.log_timing(self.operation, round(duration_ms, 2))