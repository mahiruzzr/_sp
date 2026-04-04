"use client";

import { useEffect, useState, useTransition } from "react";
import { Activity, Radar, ScrollText } from "lucide-react";

import { ReportViewer } from "@/components/report-viewer";
import { StatusList } from "@/components/status-list";
import { MissionForm } from "@/components/mission-form";
import { taskRunClient } from "@/lib/api-client";
import type { TaskRunResponse } from "@/lib/types";

export default function HomePage() {
  const [run, setRun] = useState<TaskRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [isSubmitting, startTransition] = useTransition();

  const handleSubmit = async (payload: {
    instruction: string;
    context?: string;
    reportTitle?: string;
  }) => {
    setError(null);
    setRun(null);
    setActiveTaskId(null);

    try {
      const response = await taskRunClient.createRun(payload);
      startTransition(() => {
        setRun(response);
        setActiveTaskId(response.task_id);
      });
    } catch (submissionError) {
      const message =
        submissionError instanceof Error ? submissionError.message : "Failed to start the task.";
      setError(message);
    }
  };

  useEffect(() => {
    if (!activeTaskId) {
      return;
    }

    let cancelled = false;
    let timer: ReturnType<typeof window.setTimeout> | null = null;

    const poll = async () => {
      try {
        const next = await taskRunClient.getRun(activeTaskId);
        if (cancelled) {
          return;
        }

        startTransition(() => {
          setRun(next);
        });

        if (next.status === "completed" || next.status === "failed") {
          setActiveTaskId(null);
          return;
        }

        timer = window.setTimeout(() => {
          void poll();
        }, 2000);
      } catch (pollingError) {
        if (cancelled) {
          return;
        }

        const message = pollingError instanceof Error ? pollingError.message : "Polling failed.";
        setError(message);
        setActiveTaskId(null);
      }
    };

    void poll();

    return () => {
      cancelled = true;
      if (timer !== null) {
        window.clearTimeout(timer);
      }
    };
  }, [activeTaskId, startTransition]);

  const stageList = run?.stages ?? [
    { name: "Researcher", order: 1, status: "pending" as const, message: "Waiting to run.", started_at: null, finished_at: null },
    { name: "Analyst", order: 2, status: "pending" as const, message: "Waiting to run.", started_at: null, finished_at: null },
    { name: "Writer", order: 3, status: "pending" as const, message: "Waiting to run.", started_at: null, finished_at: null },
  ];

  const isBusy = run?.status === "queued" || run?.status === "running" || isSubmitting;

  return (
    <main className="min-h-screen px-6 py-10 md:px-10 xl:px-16">
      <div className="mx-auto max-w-7xl space-y-8">
        <section className="panel-glow rounded-[2rem] border border-cyan-400/20 bg-slate-950/70 p-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-4">
              <span className="inline-flex rounded-full border border-cyan-400/20 bg-cyan-500/10 px-4 py-1 text-sm font-medium uppercase tracking-[0.25em] text-cyan-200">
                Cyberpunk Command Deck
              </span>
              <div className="space-y-3">
                <h1 className="max-w-4xl font-[family-name:var(--font-display)] text-4xl leading-tight text-white md:text-6xl">
                  AgentOrchestrator coordinates Researcher, Analyst, and Writer into one live AI workflow.
                </h1>
                <p className="max-w-3xl text-lg leading-8 text-slate-300">
                  Launch a complex task, watch the agents move through the pipeline in real time, and receive a structured Markdown report without blocking the UI.
                </p>
              </div>
            </div>

            <div className="grid gap-3 text-sm text-slate-300 sm:grid-cols-3">
              <div className="rounded-2xl border border-cyan-400/15 bg-slate-900/80 px-4 py-3">
                <Radar className="mb-2 h-4 w-4 text-cyan-300" />
                <p className="font-[family-name:var(--font-display)] text-xs uppercase tracking-[0.25em] text-cyan-100">Research</p>
                <p className="mt-1 text-slate-400">Tavily-backed web discovery for current signals.</p>
              </div>
              <div className="rounded-2xl border border-fuchsia-400/15 bg-slate-900/80 px-4 py-3">
                <Activity className="mb-2 h-4 w-4 text-fuchsia-300" />
                <p className="font-[family-name:var(--font-display)] text-xs uppercase tracking-[0.25em] text-fuchsia-100">Analysis</p>
                <p className="mt-1 text-slate-400">Structured reasoning, tradeoffs, and implications.</p>
              </div>
              <div className="rounded-2xl border border-emerald-400/15 bg-slate-900/80 px-4 py-3">
                <ScrollText className="mb-2 h-4 w-4 text-emerald-300" />
                <p className="font-[family-name:var(--font-display)] text-xs uppercase tracking-[0.25em] text-emerald-100">Writer</p>
                <p className="mt-1 text-slate-400">Professional Markdown report assembly.</p>
              </div>
            </div>
          </div>
        </section>

        <div className="grid gap-8 xl:grid-cols-[0.95fr_1.05fr]">
          <section className="space-y-6">
            <div className="panel-glow rounded-[1.75rem] border border-cyan-400/20 bg-slate-950/70 p-6">
              <MissionForm onSubmit={handleSubmit} isSubmitting={isBusy} />
              {error ? (
                <div className="mt-4 rounded-2xl border border-rose-400/25 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
                  {error}
                </div>
              ) : null}
            </div>

            <StatusList
              stages={stageList}
              progressMessage={run?.progress_message ?? "Awaiting a new mission briefing."}
              currentAgent={run?.current_agent ?? null}
              isBusy={isBusy}
            />
          </section>

          <section>
            <ReportViewer result={run} isLoading={isBusy} />
          </section>
        </div>
      </div>
    </main>
  );
}
