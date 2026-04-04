import asyncio
import logging
import traceback
from functools import lru_cache
from uuid import uuid4

from app.core.config import Settings, get_settings
from app.models.schemas import TaskRunRequest, TaskRunResponse
from app.services.pipeline import CrewPipeline
from app.services.reporting import ReportService
from app.services.task_store import TaskRunStore

logger = logging.getLogger(__name__)


class AgentOrchestratorService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pipeline = CrewPipeline(settings)
        self.report_service = ReportService(settings)
        self.store = TaskRunStore(max_records=settings.task_store_limit)
        self._semaphore = asyncio.Semaphore(settings.max_concurrent_runs)

    async def create_run(self, payload: TaskRunRequest) -> TaskRunResponse:
        self.pipeline.validate_configuration()
        task_id = uuid4().hex[:12]
        snapshot = await self.store.create(
            task_id=task_id,
            instruction=payload.instruction,
            report_title=payload.report_title or "AgentOrchestrator Report",
        )
        background_task = asyncio.create_task(self._execute_run(task_id, payload), name=f"agent-run-{task_id}")
        background_task.add_done_callback(self._handle_background_task_done)
        return snapshot

    async def get_run(self, task_id: str) -> TaskRunResponse | None:
        return await self.store.get(task_id)

    async def _execute_run(self, task_id: str, payload: TaskRunRequest) -> None:
        try:
            self.pipeline.validate_configuration()
            async with self._semaphore:
                await self.store.start_run(task_id, "Execution slot acquired. Initializing agents.")

                await self.store.start_stage(
                    task_id,
                    "Researcher",
                    "Researcher is searching the web with Tavily for current signals.",
                )
                research_brief = await asyncio.to_thread(self.pipeline.run_research, payload)
                await self.store.complete_stage(
                    task_id,
                    "Researcher",
                    "Research complete. Handing evidence to the Analyst.",
                )

                await self.store.start_stage(
                    task_id,
                    "Analyst",
                    "Analyst is structuring findings, tradeoffs, and implications.",
                )
                analysis_brief = await asyncio.to_thread(self.pipeline.run_analysis, payload, research_brief)
                await self.store.complete_stage(
                    task_id,
                    "Analyst",
                    "Analysis complete. Handing structured insights to the Writer.",
                )

                await self.store.start_stage(
                    task_id,
                    "Writer",
                    "Writer is drafting the final professional Markdown report.",
                )
                markdown_report = await asyncio.to_thread(
                    self.pipeline.run_writer,
                    payload,
                    task_id,
                    research_brief,
                    analysis_brief,
                )
                await self.store.complete_stage(
                    task_id,
                    "Writer",
                    "Writing complete. Finalizing report metadata and storage.",
                )

                report_path = None
                if payload.save_report:
                    report_path = await asyncio.to_thread(
                        self.report_service.persist,
                        task_id,
                        markdown_report,
                        payload.report_title,
                    )

                await self.store.complete_run(
                    task_id,
                    summary=self.report_service.summarize(markdown_report),
                    markdown_report=markdown_report,
                    report_path=str(report_path) if report_path else None,
                    metadata={
                        "model": self.settings.model,
                        "saved": str(bool(report_path)).lower(),
                        "agent_sequence": "Researcher -> Analyst -> Writer",
                    },
                )
        except Exception as exc:
            await self._log_and_fail_run(task_id, exc, "Background run failed unexpectedly")

    async def _log_and_fail_run(self, task_id: str, exc: Exception, message: str) -> None:
        logger.error(
            "%s for task_id=%s: %s\n%s",
            message,
            task_id,
            exc,
            traceback.format_exc(),
        )

        try:
            await self.store.fail_run(task_id, f"{message}: {exc}")
        except Exception:
            logger.error(
                "Failed to persist failed task state for task_id=%s\n%s",
                task_id,
                traceback.format_exc(),
            )

    def _handle_background_task_done(self, task: asyncio.Task[None]) -> None:
        try:
            task.result()
        except Exception as exc:
            logger.error(
                "Unhandled exception escaped the background task %s: %s\n%s",
                task.get_name(),
                exc,
                traceback.format_exc(),
            )


@lru_cache(maxsize=1)
def get_orchestrator_service() -> AgentOrchestratorService:
    return AgentOrchestratorService(get_settings())
