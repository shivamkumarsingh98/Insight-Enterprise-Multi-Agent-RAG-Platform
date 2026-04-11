# app/registry/agent_registry.py

import time
import uuid
from typing import Optional, Callable
from enum import Enum
from app.core.logging import get_logger

logger = get_logger("agent_registry")


class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"   # kaam kar raha hai but slow/errors


class AgentCapability(str, Enum):
    SEARCH = "search"
    SUMMARIZE = "summarize"
    RAG = "rag"
    CLASSIFY = "classify"
    EVALUATE = "evaluate"


class AgentMetrics:
    def __init__(self):
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.total_duration_ms = 0.0
        self.last_called_at: Optional[float] = None
        self.last_error: Optional[str] = None

    def record_success(self, duration_ms: float):
        self.total_calls += 1
        self.successful_calls += 1
        self.total_duration_ms += duration_ms
        self.last_called_at = time.time()

    def record_failure(self, error: str):
        self.total_calls += 1
        self.failed_calls += 1
        self.last_called_at = time.time()
        self.last_error = error

    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 1.0
        return self.successful_calls / self.total_calls

    @property
    def avg_duration_ms(self) -> float:
        if self.successful_calls == 0:
            return 0.0
        return self.total_duration_ms / self.successful_calls

    def to_dict(self) -> dict:
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": round(self.success_rate, 3),
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "last_called_at": self.last_called_at,
            "last_error": self.last_error
        }


class AgentRegistration:
    def __init__(
        self,
        name: str,
        version: str,
        capabilities: list[AgentCapability],
        handler: Callable,
        description: str = ""
    ):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.version = version
        self.capabilities = capabilities
        self.handler = handler
        self.description = description
        self.status = AgentStatus.ACTIVE
        self.metrics = AgentMetrics()
        self.registered_at = time.time()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "capabilities": [c.value for c in self.capabilities],
            "description": self.description,
            "status": self.status.value,
            "registered_at": self.registered_at,
            "metrics": self.metrics.to_dict()
        }


class AgentRegistry:
    """
    Dynamic registry — agents apne aap register/deregister hote hain.
    Supervisor ise use karta hai sahi agent dhundhne ke liye.
    """

    def __init__(self):
        self._agents: dict[str, AgentRegistration] = {}
        logger.info("AgentRegistry initialized")

    def register(
        self,
        name: str,
        version: str,
        capabilities: list[AgentCapability],
        handler: Callable,
        description: str = ""
    ) -> AgentRegistration:

        agent = AgentRegistration(
            name=name,
            version=version,
            capabilities=capabilities,
            handler=handler,
            description=description
        )
        self._agents[name] = agent
        logger.info("Agent registered",
            agent_name=name,
            version=version,
            capabilities=[c.value for c in capabilities]
        )
        return agent

    def deregister(self, name: str):
        if name in self._agents:
            del self._agents[name]
            logger.info("Agent deregistered", agent_name=name)

    def get(self, name: str) -> Optional[AgentRegistration]:
        agent = self._agents.get(name)
        if agent and agent.status == AgentStatus.INACTIVE:
            logger.warning("Agent is inactive", agent_name=name)
            return None
        return agent

    def get_by_capability(self, capability: AgentCapability) -> list[AgentRegistration]:
        """Koi capability chahiye — kaun kaun se agents kar sakte hain"""
        return [
            a for a in self._agents.values()
            if capability in a.capabilities
            and a.status != AgentStatus.INACTIVE
        ]

    def set_status(self, name: str, status: AgentStatus):
        if name in self._agents:
            self._agents[name].status = status
            logger.info("Agent status updated", agent_name=name, status=status.value)

    def record_call(self, name: str, success: bool, duration_ms: float, error: str = ""):
        agent = self._agents.get(name)
        if not agent:
            return
        if success:
            agent.metrics.record_success(duration_ms)
        else:
            agent.metrics.record_failure(error)

        # Auto-degrade agar success rate 50% se kam ho
        if agent.metrics.total_calls >= 5 and agent.metrics.success_rate < 0.5:
            agent.status = AgentStatus.DEGRADED
            logger.warning("Agent degraded due to low success rate",
                agent_name=name,
                success_rate=agent.metrics.success_rate
            )

    def get_all(self) -> list[dict]:
        return [a.to_dict() for a in self._agents.values()]

    def get_healthy_agents(self) -> list[dict]:
        return [
            a.to_dict() for a in self._agents.values()
            if a.status == AgentStatus.ACTIVE
        ]


# Global singleton
registry = AgentRegistry()