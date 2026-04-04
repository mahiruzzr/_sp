export type TaskLifecycleStatus = "queued" | "running" | "completed" | "failed";
export type AgentStageStatus = "pending" | "running" | "completed" | "failed";

export type AgentStageSnapshot = {
  name: string;
  order: number;
  status: AgentStageStatus;
  message: string;
  started_at: string | null;
  finished_at: string | null;
};

export type TaskRunRequest = {
  instruction: string;
  context?: string;
  reportTitle?: string;
};

export type TaskRunResponse = {
  task_id: string;
  instruction: string;
  report_title: string;
  status: TaskLifecycleStatus;
  progress_message: string;
  current_agent: string | null;
  stages: AgentStageSnapshot[];
  summary: string | null;
  markdown_report: string | null;
  report_path: string | null;
  error: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};
