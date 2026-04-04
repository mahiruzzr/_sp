# AgentOrchestrator

AgentOrchestrator is a monorepo for a three-agent AI workflow built with FastAPI, CrewAI, LangChain, Next.js, and Tailwind CSS. It accepts a complex instruction, runs a `Researcher`, `Analyst`, and `Writer` in sequence, then delivers a structured Markdown report through a cyberpunk-style web console.

## Monorepo layout

```text
.
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- models/
|   |   `-- services/
|   |-- reports/
|   `-- requirements.txt
|-- frontend/
|   |-- app/
|   |-- components/
|   `-- lib/
|-- .env.example
`-- README.md
```

## How the system works

1. The frontend sends a `POST /api/v1/run-task` request with the user instruction.
2. FastAPI immediately returns a task id and queues the run instead of waiting for the full LLM output.
3. The backend executes the workflow asynchronously:
   - `Researcher` uses `TavilySearchTool` to gather recent web evidence.
   - `Analyst` converts the research brief into structured reasoning and tradeoffs.
   - `Writer` turns the analysis into a professional Markdown report.
4. The frontend polls `GET /api/v1/run-task/{task_id}` every 2 seconds and updates the live agent status list.
5. When the workflow completes, the final Markdown report is returned and optionally written to `backend/reports/`.

## Why this architecture

- Avoids request timeout risk by moving long AI work into background async tasks.
- Limits memory growth by storing only task metadata, stage state, and the final report instead of every intermediate payload.
- Refactors prompt generation, report persistence, API access, and task-state handling into dedicated classes to keep responsibilities clear.

## Setup

### 1. Environment variables

Copy the repository template:

```bash
copy .env.example .env
```

Required values:

- `TAVILY_API_KEY`

Choose one LLM provider:

- `MODEL=gemini/gemini-3-flash-preview` with `GOOGLE_API_KEY` and `GOOGLE_API_VERSION=v1beta`
- `MODEL=groq/llama-3.1-8b-instant` with `GROQ_API_KEY`

Optional values:

- `MAX_CONCURRENT_RUNS`
- `TASK_STORE_LIMIT`
- `NEXT_PUBLIC_API_BASE_URL`

If you want the frontend to read an explicit API base URL, also copy:

```bash
copy frontend\.env.local.example frontend\.env.local
```

### 2. Start the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## API contract

### Start a run

`POST /api/v1/run-task`

Example payload:

```json
{
  "instruction": "Analyze 2026 trends in 3D rendering.",
  "context": "Focus on AI-assisted rendering, real-time ray tracing, and cloud rendering.",
  "report_title": "2026 3D Rendering Technology Trend Report",
  "save_report": true
}
```

Example response:

```json
{
  "task_id": "a1b2c3d4e5f6",
  "status": "queued",
  "progress_message": "Task accepted. Waiting for an execution slot.",
  "current_agent": null,
  "stages": [
    { "name": "Researcher", "status": "pending" },
    { "name": "Analyst", "status": "pending" },
    { "name": "Writer", "status": "pending" }
  ]
}
```

### Poll a run

`GET /api/v1/run-task/{task_id}`

When the run finishes, the response contains:

- `summary`
- `markdown_report`
- `report_path`
- per-agent stage status

## Diagnosed and fixed integration issues

- The previous backend returned the full report synchronously from one request, which risked timeout during long LLM runs. This is now asynchronous.
- The previous workflow had only two agents and no explicit Writer stage. The pipeline now runs `Researcher -> Analyst -> Writer`.
- The frontend previously blocked on a single fetch. It now starts a task, polls for status, and renders progress live.
- Reusable responsibilities were previously bundled into one orchestration service. They are now separated into `CrewPipeline`, `TaskRunStore`, `ReportService`, and `TaskRunClient`.
- Large-output handling is safer now because the backend does not keep every intermediate artifact in shared task state, and the frontend defers Markdown rendering.

## Notes

- Reports are saved under `backend/reports/` when `save_report` is `true`.
- `POST /api/v1/orchestrate` is kept as a compatibility alias for starting a task.
- The UI uses `lucide-react` icons plus custom Tailwind styling for the cyberpunk console.
