import type { TaskRunRequest, TaskRunResponse } from "@/lib/types";

const DEFAULT_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class TaskRunClient {
  constructor(private readonly apiBaseUrl: string = DEFAULT_API_BASE_URL) {}

  async createRun(payload: TaskRunRequest): Promise<TaskRunResponse> {
    return this.request<TaskRunResponse>("/api/v1/run-task", {
      method: "POST",
      body: JSON.stringify({
        instruction: payload.instruction,
        context: payload.context,
        report_title: payload.reportTitle,
        save_report: true,
      }),
    });
  }

  async getRun(taskId: string): Promise<TaskRunResponse> {
    return this.request<TaskRunResponse>(`/api/v1/run-task/${taskId}`, {
      method: "GET",
    });
  }

  private async request<T>(path: string, init: RequestInit): Promise<T> {
    const response = await fetch(`${this.apiBaseUrl}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
      },
      cache: "no-store",
    });

    if (!response.ok) {
      let message = "Request failed.";
      try {
        const errorPayload = (await response.json()) as { detail?: string };
        message = errorPayload.detail ?? message;
      } catch {
        message = response.statusText || message;
      }
      throw new Error(message);
    }

    return (await response.json()) as T;
  }
}

export const taskRunClient = new TaskRunClient();
