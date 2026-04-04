"use client";

import { useDeferredValue } from "react";
import { FileText, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import type { TaskRunResponse } from "@/lib/types";

type ReportViewerProps = {
  result: TaskRunResponse | null;
  isLoading: boolean;
};

export function ReportViewer({ result, isLoading }: ReportViewerProps) {
  const deferredMarkdown = useDeferredValue(result?.markdown_report ?? null);

  if (!result && !isLoading) {
    return (
      <div className="panel-glow flex h-full min-h-[680px] flex-col justify-between rounded-[1.75rem] border border-fuchsia-400/20 bg-slate-950/70 p-8">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-fuchsia-300/70">Report Deck</p>
          <h2 className="mt-4 font-[family-name:var(--font-display)] text-3xl text-white">
            The final Markdown report will appear here.
          </h2>
        </div>
        <div className="rounded-[1.5rem] border border-fuchsia-400/20 bg-slate-900/80 p-5">
          <p className="text-sm text-slate-400">
            Expected sections: executive summary, task framing, research findings, analysis, recommendations, risks, and next steps.
          </p>
        </div>
      </div>
    );
  }

  if (result?.status === "failed") {
    return (
      <div className="panel-glow flex min-h-[680px] flex-col justify-between rounded-[1.75rem] border border-rose-400/20 bg-slate-950/70 p-8">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-rose-300/70">Execution Failed</p>
          <h2 className="mt-4 font-[family-name:var(--font-display)] text-3xl text-white">
            The pipeline stopped before the final report was produced.
          </h2>
        </div>
        <div className="rounded-[1.5rem] border border-rose-400/20 bg-rose-500/10 p-5 text-sm text-rose-100">
          {result.error ?? "An unknown error occurred during agent execution."}
        </div>
      </div>
    );
  }

  if (!deferredMarkdown) {
    return (
      <div className="panel-glow flex h-full min-h-[680px] items-center justify-center rounded-[1.75rem] border border-cyan-400/20 bg-slate-950/70">
        <div className="space-y-4 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full border border-cyan-400/30 bg-cyan-400/10">
            <Sparkles className="h-7 w-7 animate-pulse text-cyan-300" />
          </div>
          <div>
            <p className="font-[family-name:var(--font-display)] text-lg text-white">Compiling final report</p>
            <p className="mt-2 text-sm text-slate-400">
              The Writer is packaging the analysis into a polished Markdown briefing.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[680px] space-y-6">
      <div className="panel-glow rounded-[1.75rem] border border-fuchsia-400/20 bg-slate-950/70 p-5">
        <div className="mb-4 flex items-center gap-3">
          <div className="rounded-xl border border-fuchsia-400/20 bg-fuchsia-500/10 p-2">
            <FileText className="h-4 w-4 text-fuchsia-200" />
          </div>
          <div>
            <p className="font-[family-name:var(--font-display)] text-sm uppercase tracking-[0.25em] text-fuchsia-100">
              Final Report
            </p>
            <p className="text-sm text-slate-400">Rendered from the Writer agent's Markdown output.</p>
          </div>
        </div>

        <div className="flex flex-col gap-2 text-sm text-slate-300">
          <span>
            <strong>Task ID:</strong> {result.task_id}
          </span>
          <span>
            <strong>Status:</strong> {result.status}
          </span>
          {result.summary ? (
            <span>
              <strong>Summary:</strong> {result.summary}
            </span>
          ) : null}
          {result.report_path ? (
            <span className="break-all">
              <strong>Saved Report:</strong> {result.report_path}
            </span>
          ) : null}
        </div>
      </div>

      <article className="prose-report panel-glow rounded-[1.75rem] border border-cyan-400/20 bg-slate-950/80 p-8">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{deferredMarkdown}</ReactMarkdown>
      </article>
    </div>
  );
}
