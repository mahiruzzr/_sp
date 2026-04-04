from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class TaskLifecycleStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    instruction: str = Field(
        ...,
        min_length=10,
        validation_alias=AliasChoices("instruction", "task"),
        serialization_alias="instruction",
        description="The complex task to be handled by the multi-agent workflow.",
    )
    context: str | None = Field(default=None, description="Optional background context or constraints.")
    report_title: str | None = Field(
        default="AgentOrchestrator Report",
        description="Optional title for the generated report.",
    )
    save_report: bool = Field(default=True, description="Persist the final Markdown report to disk.")


class AgentStageSnapshot(BaseModel):
    name: str
    order: int
    status: AgentStageStatus
    message: str
    started_at: datetime | None = None
    finished_at: datetime | None = None


class TaskRunResponse(BaseModel):
    task_id: str
    instruction: str
    report_title: str
    status: TaskLifecycleStatus
    progress_message: str
    current_agent: str | None = None
    stages: list[AgentStageSnapshot]
    summary: str | None = None
    markdown_report: str | None = None
    report_path: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
