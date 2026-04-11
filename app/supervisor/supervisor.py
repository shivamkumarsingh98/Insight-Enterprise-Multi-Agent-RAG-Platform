# app/supervisor/supervisor.py

import time
import uuid
from typing import Optional
from app.registry.agent_registry import registry, AgentCapability, AgentStatus
from app.memory.short_term import memory
from app.memory.long_term import long_term_memory
from app.core.config import settings
from app.core.logging import get_logger, TimingContext
from app.agents.classifier_agent import classifier
from app.core.circuit_breaker import circuit_registry

logger = get_logger("supervisor")


class TaskResult:
    def __init__(self, task_id: str, agent_name: str, success: bool,
                 data: any = None, error: str = "", duration_ms: float = 0):
        self.task_id = task_id
        self.agent_name = agent_name
        self.success = success
        self.data = data
        self.error = error
        self.duration_ms = duration_ms

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "success": self.success,
            "error": self.error,
            "duration_ms": self.duration_ms
        }


class Task:
    def __init__(self, name: str, capability: AgentCapability,
                 input_data: any, depends_on: list[str] = []):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.capability = capability
        self.input_data = input_data
        self.depends_on = depends_on
        self.status = "pending"
        self.result: Optional[TaskResult] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "capability": self.capability.value,
            "status": self.status,
            "depends_on": self.depends_on
        }


class SupervisorAgent:

    def __init__(self):
        self.execution_history: list[dict] = []
        logger.info("SupervisorAgent initialized")

    def decompose(self, query: str, intent: str = "research_search") -> list[Task]:
        tasks = []

        if intent == "deep_research":
            research_task = Task(
                name="deep_research",
                capability=AgentCapability.RAG,
                input_data={"query": query},
                depends_on=[]
            )
            tasks.append(research_task)

        else:
            search_task = Task(
                name="search",
                capability=AgentCapability.SEARCH,
                input_data={"query": query},
                depends_on=[]
            )
            tasks.append(search_task)

            summarize_task = Task(
                name="summarize",
                capability=AgentCapability.SUMMARIZE,
                input_data=None,
                depends_on=[search_task.id]
            )
            tasks.append(summarize_task)

        logger.info("Tasks decomposed",
            query=query,
            intent=intent,
            task_count=len(tasks),
            tasks=[t.name for t in tasks]
        )
        return tasks

    def _select_agent(self, capability: AgentCapability) -> Optional[any]:
        agents = registry.get_by_capability(capability)
        if not agents:
            logger.error("No agent found for capability", capability=capability.value)
            return None
        best = min(agents, key=lambda a: a.metrics.failed_calls)
        return best

    def _execute_task(self, task: Task, context: dict) -> TaskResult:
        agent_reg = self._select_agent(task.capability)

        if not agent_reg:
            return TaskResult(
                task_id=task.id,
                agent_name="none",
                success=False,
                error=f"No agent available for {task.capability.value}"
            )

        # Circuit breaker — is agent ke liye
        breaker = circuit_registry.get_or_create(
            agent_reg.name,
            failure_threshold=5,
            recovery_timeout=30
        )

        last_error = ""

        for attempt in range(1, settings.MAX_RETRIES + 1):
            start = time.time()

            try:
                logger.info(
                    "Executing task",
                    task=task.name,
                    agent=agent_reg.name,
                    attempt=attempt
                )

                input_data = task.input_data or context.get("last_result")

                # Circuit breaker ke through call karo
                if task.capability == AgentCapability.SEARCH:
                    result = breaker.call(agent_reg.handler, input_data["query"])

                elif task.capability == AgentCapability.SUMMARIZE:
                    results = []
                    for paper in input_data:
                        summary = breaker.call(agent_reg.handler, paper)
                        results.append({
                            "title": paper.get("title", ""),
                            "summary": summary,
                            "link": paper.get("link", "")
                        })
                    result = results

                else:
                    result = breaker.call(agent_reg.handler, input_data)

                duration_ms = round((time.time() - start) * 1000, 2)
                registry.record_call(agent_reg.name, True, duration_ms)

                logger.info(
                    "Task completed",
                    task=task.name,
                    agent=agent_reg.name,
                    duration_ms=duration_ms
                )

                return TaskResult(
                    task_id=task.id,
                    agent_name=agent_reg.name,
                    success=True,
                    data=result,
                    duration_ms=duration_ms
                )

            except Exception as e:
                last_error = str(e)
                duration_ms = round((time.time() - start) * 1000, 2)

                registry.record_call(agent_reg.name, False, duration_ms, last_error)

                logger.error(
                    "Task failed",
                    task=task.name,
                    agent=agent_reg.name,
                    attempt=attempt,
                    error=last_error
                )

                # Circuit OPEN hai — retry mat karo
                if "Circuit OPEN" in last_error:
                    break

                if attempt < settings.MAX_RETRIES:
                    time.sleep(settings.RETRY_DELAY_SECONDS * attempt)

        return TaskResult(
            task_id=task.id,
            agent_name=agent_reg.name,
            success=False,
            error=last_error
        )

    def run(self, query: str, session_id: Optional[str] = None,
            user_id: Optional[str] = None,
            intent: str = "research_search") -> dict:

        run_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        logger.info("Supervisor run started",
            run_id=run_id, query=query,
            session_id=session_id, intent=intent
        )

        # Session memory
        session = memory.get_or_create(session_id)
        session.add_message("user", query)

        tasks = self.decompose(query, intent=intent)

        # ✅ Classifier — intent detect karo
        classification = classifier.classify(query)
        intent = classification.intent.value
        logger.info("Intent detected",
            intent=intent,
            confidence=classification.confidence
        )

        # ✅ Intent ke hisaab se tasks banao
        tasks = self.decompose(query, intent=intent)
        context = {}
        results = []
        failed_tasks = []

        for task in tasks:
            deps_ok = all(
                t.status == "done"
                for t in tasks
                if t.id in task.depends_on
            )
            if not deps_ok:
                task.status = "failed"
                failed_tasks.append(task.name)
                logger.error("Task skipped — dependency failed", task=task.name)
                continue

            task.status = "running"
            task_result = self._execute_task(task, context)
            task.result = task_result

            if task_result.success:
                task.status = "done"
                context["last_result"] = task_result.data
                if task.name in ("summarize", "deep_research"):
                    results = task_result.data if isinstance(task_result.data, list) else [task_result.data]
            else:
                task.status = "failed"
                failed_tasks.append(task.name)
                if task.name == "search":
                    logger.warning("Search failed — returning empty results")
                    break

        total_duration_ms = round((time.time() - start_time) * 1000, 2)

        session.add_message("assistant",
            f"Found {len(results)} results for: {query}",
            metadata={"run_id": run_id, "result_count": len(results)}
        )

        if user_id:
            long_term_memory.save_query_history(user_id, query, len(results))

        execution_record = {
            "run_id": run_id,
            "query": query,
            "intent": intent,
            "session_id": session.session_id,
            "tasks": [t.to_dict() for t in tasks],
            "result_count": len(results),
            "failed_tasks": failed_tasks,
            "total_duration_ms": total_duration_ms,
            "timestamp": time.time()
        }
        self.execution_history.append(execution_record)

        logger.info("Supervisor run completed",
            run_id=run_id,
            result_count=len(results),
            failed_tasks=failed_tasks,
            total_duration_ms=total_duration_ms
        )

        return {
            "run_id": run_id,
            "session_id": session.session_id,
            "query": query,
            "intent": intent,
            "results": results,
            "meta": {
                "total_duration_ms": total_duration_ms,
                "tasks_completed": len([t for t in tasks if t.status == "done"]),
                "tasks_failed": len(failed_tasks)
            }
        }


# Global singleton
supervisor = SupervisorAgent()