from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import TaskRunRequest, TaskRunResponse
from app.services.orchestrator import AgentOrchestratorService, get_orchestrator_service

router = APIRouter(prefix="/api/v1", tags=["agent-orchestrator"])


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/run-task", response_model=TaskRunResponse, status_code=status.HTTP_202_ACCEPTED)
@router.post("/orchestrate", response_model=TaskRunResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_task(
    payload: TaskRunRequest,
    orchestrator: AgentOrchestratorService = Depends(get_orchestrator_service),
) -> TaskRunResponse:
    try:
        return await orchestrator.create_run(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/run-task/{task_id}", response_model=TaskRunResponse)
async def get_task_status(
    task_id: str,
    orchestrator: AgentOrchestratorService = Depends(get_orchestrator_service),
) -> TaskRunResponse:
    task = await orchestrator.get_run(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' was not found.")
    return task
