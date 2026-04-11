# app/core/circuit_breaker.py

import time
from enum import Enum
from app.core.logging import get_logger

logger = get_logger("circuit_breaker")


class CircuitState(str, Enum):
    CLOSED = "closed"       # Normal — sab calls allow
    OPEN = "open"           # Failed — sab calls block
    HALF_OPEN = "half_open" # Testing — ek call allow karke dekho


class CircuitBreaker:
    """
    Circuit breaker pattern.
    Agar agent baar baar fail ho raha hai — calls band karo.
    Kuch time baad automatically retry karo.
    """

    def __init__(self, name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 30,
                 success_threshold: int = 2):
        self.name = name
        self.failure_threshold = failure_threshold   # kitne fails pe open ho
        self.recovery_timeout = recovery_timeout     # seconds — phir try karo
        self.success_threshold = success_threshold   # half-open mein kitne success chahiye

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0

        logger.info("CircuitBreaker created", name=name)

    def call(self, func, *args, **kwargs):
        """Protected function call"""

        if self.state == CircuitState.OPEN:
            # Recovery timeout check karo
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info("Circuit half-open — testing recovery", name=self.name)
            else:
                remaining = round(self.recovery_timeout - (time.time() - self.last_failure_time))
                raise Exception(
                    f"Circuit OPEN for '{self.name}'. "
                    f"Retry in {remaining}s"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(str(e))
            raise

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("Circuit CLOSED — service recovered", name=self.name)
        else:
            self.failure_count = 0

    def _on_failure(self, error: str):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("Circuit OPEN — too many failures",
                name=self.name,
                failures=self.failure_count,
                error=error
            )
        else:
            logger.warning("Circuit failure recorded",
                name=self.name,
                failures=self.failure_count,
                threshold=self.failure_threshold
            )

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time
        }


class CircuitBreakerRegistry:
    """Saare circuit breakers ek jagah"""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}

    def get_or_create(self, name: str, **kwargs) -> CircuitBreaker:
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name, **kwargs)
        return self._breakers[name]

    def get_all_status(self) -> list[dict]:
        return [b.get_status() for b in self._breakers.values()]


# Global singleton
circuit_registry = CircuitBreakerRegistry()