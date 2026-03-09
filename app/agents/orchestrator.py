"""
Modular Agent Framework - Orchestrator, Planner, and Tool Registry

Implements Clean Architecture for AI agent execution:
- TaskPlanner: breaks user input into structured steps
- ToolRegistry: manages and dispatches tool calls
- AgentOrchestrator: coordinates planning and execution
- DeepResearchAgent: specialised orchestrator for deep research tasks
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, NamedTuple, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class PlanStep(NamedTuple):
    """A single step in an agent execution plan."""

    tool: str
    args: Dict[str, Any]
    description: str = ""


# ---------------------------------------------------------------------------
# TaskPlanner
# ---------------------------------------------------------------------------

class TaskPlanner:
    """Generates a structured execution plan from free-form user input."""

    SUPPORTED_TOOLS = [
        "web_search",
        "document_reader",
        "summarizer",
        "code_executor",
    ]

    # Keywords that suggest a web search step is needed
    WEB_SEARCH_KEYWORDS = (
        "pesquisar", "buscar", "search", "find",
        "what is", "o que é", "quem", "quando",
        "onde", "qual", "noticia", "noticias",
        "hoje", "atual", "preco", "cotacao",
    )

    # Keywords that suggest a document reader step is needed
    DOCUMENT_KEYWORDS = (
        "documento", "document", "pdf", "ler", "read",
    )

    def __init__(self, model: str = "gpt-4o"):
        self.model = model

    def generate_steps(self, user_input: str) -> List[PlanStep]:
        """Break *user_input* into an ordered list of :class:`PlanStep` objects.

        The default implementation uses simple keyword heuristics.  When an
        OpenAI key is available the planner delegates to the LLM for richer
        planning (stub – extend in production).
        """
        steps: List[PlanStep] = []
        text = (user_input or "").lower()

        if any(kw in text for kw in self.WEB_SEARCH_KEYWORDS):
            steps.append(PlanStep(tool="web_search", args={"query": user_input}, description="Search the web"))

        if any(kw in text for kw in self.DOCUMENT_KEYWORDS):
            steps.append(PlanStep(tool="document_reader", args={"query": user_input}, description="Read documents"))

        steps.append(PlanStep(tool="summarizer", args={"query": user_input}, description="Synthesise results"))

        return steps


# ---------------------------------------------------------------------------
# ToolRegistry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Central registry that manages available tools and dispatches calls."""

    def __init__(self, enabled_tools: Optional[List[str]] = None):
        self._tools: Dict[str, Any] = {}
        self._register_defaults()
        if enabled_tools is not None:
            # Restrict to explicitly enabled tools only
            self._tools = {k: v for k, v in self._tools.items() if k in enabled_tools}

    # ------------------------------------------------------------------
    # Registration helpers
    # ------------------------------------------------------------------

    def _register_defaults(self):
        """Register built-in tool handlers."""
        self._tools = {
            "web_search": self._tool_web_search,
            "document_reader": self._tool_document_reader,
            "summarizer": self._tool_summarizer,
            "code_executor": self._tool_code_executor,
        }

    def register(self, name: str, handler) -> None:
        """Register a custom tool handler at runtime."""
        self._tools[name] = handler

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def call(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Call *tool_name* with *args* and return its result dict."""
        handler = self._tools.get(tool_name)
        if handler is None:
            logger.warning("Tool '%s' is not registered – skipping.", tool_name)
            return {"tool": tool_name, "result": None, "error": "tool_not_found"}
        try:
            return handler(**args)
        except Exception as exc:
            logger.exception("Tool '%s' raised an exception.", tool_name)
            return {"tool": tool_name, "result": None, "error": str(exc)}

    # ------------------------------------------------------------------
    # Built-in tool implementations
    # ------------------------------------------------------------------

    def _tool_web_search(self, query: str, **_) -> Dict[str, Any]:
        if not settings.web_search_enabled:
            return {"tool": "web_search", "result": None, "error": "web_search_disabled"}
        try:
            from app.services.web_search_service import WebSearchService

            svc = WebSearchService()
            result = svc.search(query)
            return {"tool": "web_search", "result": result}
        except Exception as exc:
            logger.exception("web_search tool failed.")
            return {"tool": "web_search", "result": None, "error": str(exc)}

    def _tool_document_reader(self, query: str, **_) -> Dict[str, Any]:
        return {"tool": "document_reader", "result": f"Document context for: {query}"}

    def _tool_summarizer(self, query: str, **_) -> Dict[str, Any]:
        return {"tool": "summarizer", "result": f"Summary for: {query}"}

    def _tool_code_executor(self, code: str = "", **_) -> Dict[str, Any]:
        return {"tool": "code_executor", "result": f"Execution result for: {code[:100]}"}


# ---------------------------------------------------------------------------
# AgentOrchestrator
# ---------------------------------------------------------------------------

class AgentOrchestrator:
    """Central orchestrator that coordinates planning and tool execution.

    Example::

        orchestrator = AgentOrchestrator()
        result = orchestrator.execute("Search for AI trends in 2025")
    """

    def __init__(self, model: str = "gpt-4o"):
        self.planner = TaskPlanner(model)
        self.tools = ToolRegistry(["web_search", "document_reader", "summarizer"])

    def execute(self, user_input: str) -> Dict[str, Any]:
        """Execute *user_input* by planning steps and calling the required tools."""
        plan = self.planner.generate_steps(user_input)
        results: List[Dict[str, Any]] = []

        for step in plan:
            result = self.tools.call(step.tool, step.args)
            results.append(result)
            logger.debug("Step '%s' completed: %s", step.tool, result)

        return self.synthesize(plan, results)

    def synthesize(self, plan: List[PlanStep], results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine step results into a final response payload."""
        successful = [r for r in results if r.get("result") is not None]
        combined_content = " | ".join(
            str(r["result"]) for r in successful if r.get("result")
        )
        return {
            "content": combined_content or "No results found.",
            "steps_executed": len(plan),
            "steps_successful": len(successful),
            "plan": [{"tool": s.tool, "description": s.description} for s in plan],
        }


# ---------------------------------------------------------------------------
# DeepResearchAgent (specialised orchestrator)
# ---------------------------------------------------------------------------

class DeepResearchAgent:
    """Specialised agent for deep research tasks used by the Celery worker.

    Wraps :class:`AgentOrchestrator` and binds execution to a *session_id*
    for persistence and status tracking.
    """

    def __init__(self, session_id: str, model: str = "gpt-4o"):
        self.session_id = session_id
        self.orchestrator = AgentOrchestrator(model=model)

    def execute(self, query: str) -> Dict[str, Any]:
        """Run the research pipeline for *query* and return a result dict."""
        logger.info("DeepResearchAgent [%s] executing query: %.80s", self.session_id, query)
        result = self.orchestrator.execute(query)
        result["session_id"] = self.session_id
        return result
