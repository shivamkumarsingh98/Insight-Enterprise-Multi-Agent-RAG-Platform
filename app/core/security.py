# app/core/security.py

from fastapi import Request, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings
from app.core.logging import get_logger
import time

logger = get_logger("security")

api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)

# Role definitions
ROLES = {
    "admin": ["search", "generate-pdf", "agents", "session", "memory", "evaluate", "audit"],
    "user":  ["search", "generate-pdf", "session"],
    "readonly": ["search", "session"],
}

# API key → role mapping (in production: load from DB/Redis)
API_KEY_ROLES: dict = {}

def _build_key_map():
    keys = settings.API_KEYS.split(",")
    roles = settings.API_KEY_ROLES.split(",") if settings.API_KEY_ROLES else []
    for i, key in enumerate(keys):
        role = roles[i] if i < len(roles) else "user"
        API_KEY_ROLES[key.strip()] = role.strip()

_build_key_map()


def get_api_key(request: Request) -> str:
    key = request.headers.get(settings.API_KEY_HEADER)
    if not key:
        logger.warning("Missing API key", path=request.url.path)
        raise HTTPException(status_code=401, detail="API key required")
    if key not in API_KEY_ROLES:
        logger.warning("Invalid API key attempt", path=request.url.path)
        raise HTTPException(status_code=403, detail="Invalid API key")
    return key


def require_role(required_role: str):
    """Decorator-style dependency for role checking"""
    def checker(request: Request):
        key = get_api_key(request)
        role = API_KEY_ROLES.get(key, "readonly")
        allowed = ROLES.get(role, [])
        # Extract route name from path
        path_parts = request.url.path.strip("/").split("/")
        route = path_parts[0] if path_parts else ""
        if route not in allowed and required_role != "any":
            logger.warning("Unauthorized access attempt",
                role=role, path=request.url.path)
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return {"key": key, "role": role}
    return checker