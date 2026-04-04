# AgentOrchestrator

AgentOrchestrator 是一個 Monorepo 多代理人 AI 工作流專案，使用 FastAPI、CrewAI、LangChain、Next.js 與 Tailwind CSS 建構。它可以接收一個複雜指令，依序啟動 `Researcher`、`Analyst` 與 `Writer` 三個代理人，最後透過具 Cyberpunk 風格的網頁介面輸出一份結構化 Markdown 報告。

## Monorepo 結構

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

## 系統如何運作

1. 前端會將使用者指令送到 `POST /api/v1/run-task`。
2. FastAPI 會立即回傳一個 task id，並將任務加入佇列，而不是等待整個 LLM 流程完成後才回應。
3. 後端會以非同步方式執行工作流：
   - `Researcher` 使用 `TavilySearchTool` 蒐集最新的網路資訊。
   - `Analyst` 將研究結果整理成結構化分析與取捨判斷。
   - `Writer` 把分析內容撰寫成專業 Markdown 報告。
4. 前端每 2 秒輪詢一次 `GET /api/v1/run-task/{task_id}`，即時更新代理人執行狀態清單。
5. 當流程完成後，系統會回傳最終 Markdown 報告，並可選擇寫入 `backend/reports/`。

## 為什麼採用這種架構

- 透過把長時間 AI 任務移到背景非同步執行，避免請求逾時。
- 只保存任務中繼資料、階段狀態與最終報告，避免因保存過多中間結果而造成記憶體成長。
- 將 prompt 生成、報告儲存、API 存取與任務狀態管理拆成獨立類別，讓職責更清楚。

## 設定方式

### 1. 環境變數

先複製專案模板：

```bash
copy .env.example .env
```

必要欄位：

- `TAVILY_API_KEY`

選擇一種 LLM 供應商：

- `MODEL=gemini/gemini-3-flash-preview`，搭配 `GOOGLE_API_KEY` 與 `GOOGLE_API_VERSION=v1beta`
- `MODEL=groq/llama-3.1-8b-instant`，搭配 `GROQ_API_KEY`

可選欄位：

- `MAX_CONCURRENT_RUNS`
- `TASK_STORE_LIMIT`
- `NEXT_PUBLIC_API_BASE_URL`

如果你希望前端明確讀取 API Base URL，也可以另外執行：

```bash
copy frontend\.env.local.example frontend\.env.local
```

### 2. 啟動後端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 啟動前端

```bash
cd frontend
npm install
npm run dev
```

然後打開 [http://localhost:3000](http://localhost:3000)。

## API 規格

### 啟動任務

`POST /api/v1/run-task`

請求範例：

```json
{
  "instruction": "分析 2026 年 3D 渲染技術的趨勢。",
  "context": "聚焦 AI 輔助渲染、即時光線追蹤與雲端渲染。",
  "report_title": "2026 3D Rendering Technology Trend Report",
  "save_report": true
}
```

回應範例：

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

### 查詢任務狀態

`GET /api/v1/run-task/{task_id}`

當任務完成後，回應會包含：

- `summary`
- `markdown_report`
- `report_path`
- 每個代理人的階段狀態

## 已診斷並修正的整合問題

- 舊版後端會在單一請求中同步回傳整份報告，容易在長時間 LLM 執行時發生逾時；現在已改為非同步處理。
- 舊版工作流只有兩個代理人，且沒有明確的 Writer 階段；現在改為 `Researcher -> Analyst -> Writer`。
- 前端原本會被單次請求阻塞；現在改為先建立任務、再輪詢狀態，並即時渲染進度。
- 原本許多可重用職責被集中在單一 orchestration service 中；現在已拆分為 `CrewPipeline`、`TaskRunStore`、`ReportService` 與 `TaskRunClient`。
- 針對大型輸出資料的處理更安全，因為後端不再把所有中間結果都保存在共享任務狀態中，前端也改用延後 Markdown 渲染以降低負擔。

