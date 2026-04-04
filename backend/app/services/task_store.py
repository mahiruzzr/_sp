from __future__ import annotations

from asyncio import Lock
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.models.schemas import (
    AgentStageSnapshot,
    AgentStageStatus,
    TaskLifecycleStatus,
    TaskRunResponse,
)


STAGE_ORDER = ("Researcher", "Analyst", "Writer")


@dataclass(slots=True)
class AgentStageRecord:
    name: str
    order: int
    status: AgentStageStatus = AgentStageStatus.PENDING
    message: str = "Waiting to run."
    started_at: datetime | None = None
    finished_at: datetime | None = None


@dataclass(slots=True)
class TaskRunRecord:
    task_id: str
    instruction: str
    report_title: str
    status: TaskLifecycleStatus
    progress_message: str
    stages: list[AgentStageRecord]
    current_agent: str | None = None
    summary: str | None = None
    markdown_report: str | None = None
    report_path: str | None = None
    error: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class TaskRunStore:
    def __init__(self, max_records: int = 50) -> None:
        self._max_records = max_records
        self._records: dict[str, TaskRunRecord] = {}
        self._lock = Lock()

    async def create(self, task_id: str, instruction: str, report_title: str) -> TaskRunResponse:
        async with self._lock:
            record = TaskRunRecord(
                task_id=task_id,
                instruction=instruction,
                report_title=report_title,
                status=TaskLifecycleStatus.QUEUED,
                progress_message="Task accepted. Waiting for an execution slot.",
                stages=[
                    AgentStageRecord(name=name, order=index + 1)
                    for index, name in enumerate(STAGE_ORDER)
                ],
            )
            self._records[task_id] = record
            self._prune_unlocked()
            return self._snapshot(record)

    async def get(self, task_id: str) -> TaskRunResponse | None:
        async with self._lock:
            record = self._records.get(task_id)
            return self._snapshot(record) if record else None

    async def start_run(self, task_id: str, message: str) -> None:
        async with self._lock:
            record = self._records[task_id]
            record.status = TaskLifecycleStatus.RUNNING
            record.progress_message = message
            record.updated_at = datetime.now(UTC)

    async def start_stage(self, task_id: str, stage_name: str, message: str) -> None:
        async with self._lock:
            record = self._records[task_id]
            record.status = TaskLifecycleStatus.RUNNING
            record.current_agent = stage_name
            record.progress_message = message
            record.updated_at = datetime.now(UTC)

            stage = self._find_stage(record, stage_name)
            stage.status = AgentStageStatus.RUNNING
            stage.message = message
            stage.started_at = stage.started_at or datetime.now(UTC)
            stage.finished_at = None

    async def complete_stage(self, task_id: str, stage_name: str, message: str) -> None:
        async with self._lock:
            record = self._records[task_id]
            record.progress_message = message
            record.updated_at = datetime.now(UTC)

            stage = self._find_stage(record, stage_name)
            stage.status = AgentStageStatus.COMPLETED
            stage.message = message
            stage.finished_at = datetime.now(UTC)

    async def complete_run(
        self,
        task_id: str,
        *,
        summary: str,
        markdown_report: str,
        report_path: str | None,
        metadata: dict[str, str],
    ) -> None:
        async with self._lock:
            record = self._records[task_id]
            record.status = TaskLifecycleStatus.COMPLETED
            record.current_agent = None
            record.progress_message = "All agents completed. Final report is ready."
            record.summary = summary
            record.markdown_report = markdown_report
            record.report_path = report_path
            record.metadata = metadata
            record.updated_at = datetime.now(UTC)

    async def fail_run(self, task_id: str, error_message: str) -> None:
        async with self._lock:
            record = self._records[task_id]
            record.status = TaskLifecycleStatus.FAILED
            record.progress_message = "Task failed before the report could be completed."
            record.error = error_message
            record.updated_at = datetime.now(UTC)

            if record.current_agent:
                stage = self._find_stage(record, record.current_agent)
                stage.status = AgentStageStatus.FAILED
                stage.message = error_message
                stage.finished_at = datetime.now(UTC)

            record.current_agent = None

    def _find_stage(self, record: TaskRunRecord, stage_name: str) -> AgentStageRecord:
        for stage in record.stages:
            if stage.name == stage_name:
                return stage
        raise KeyError(f"Unknown stage: {stage_name}")

    def _snapshot(self, record: TaskRunRecord | None) -> TaskRunResponse | None:
        if record is None:
            return None

        return TaskRunResponse(
            task_id=record.task_id,
            instruction=record.instruction,
            report_title=record.report_title,
            status=record.status,
            progress_message=record.progress_message,
            current_agent=record.current_agent,
            stages=[
                AgentStageSnapshot(
                    name=stage.name,
                    order=stage.order,
                    status=stage.status,
                    message=stage.message,
                    started_at=stage.started_at,
                    finished_at=stage.finished_at,
                )
                for stage in record.stages
            ],
            summary=record.summary,
            markdown_report=record.markdown_report,
            report_path=record.report_path,
            error=record.error,
            metadata=record.metadata,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def _prune_unlocked(self) -> None:
        if len(self._records) <= self._max_records:
            return

        removable = sorted(
            (
                record
                for record in self._records.values()
                if record.status in {TaskLifecycleStatus.COMPLETED, TaskLifecycleStatus.FAILED}
            ),
            key=lambda record: record.updated_at,
        )

        while len(self._records) > self._max_records and removable:
            expired = removable.pop(0)
            self._records.pop(expired.task_id, None)
