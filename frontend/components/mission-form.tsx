"use client";

import { FormEvent, useState } from "react";
import { Cpu, Sparkles } from "lucide-react";

type MissionFormProps = {
  onSubmit: (payload: { instruction: string; context?: string; reportTitle?: string }) => Promise<void>;
  isSubmitting: boolean;
};

const SAMPLE_TASK =
  "Analyze 2026 trends in 3D rendering, with emphasis on AI-assisted rendering, real-time ray tracing, cloud rendering, and the differences between gaming and film pipelines.";

export function MissionForm({ onSubmit, isSubmitting }: MissionFormProps) {
  const [instruction, setInstruction] = useState(SAMPLE_TASK);
  const [context, setContext] = useState(
    "Focus on technical maturity, major vendor moves, performance bottlenecks, and the most important opportunities to track over the next 12 months."
  );
  const [reportTitle, setReportTitle] = useState("2026 3D Rendering Technology Trend Report");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onSubmit({
      instruction,
      context: context || undefined,
      reportTitle: reportTitle || undefined,
    });
  };

  return (
    <form className="space-y-5" onSubmit={handleSubmit}>
      <div className="rounded-[1.75rem] border border-cyan-400/20 bg-slate-950/70 p-5">
        <div className="flex items-center gap-3 text-cyan-200">
          <Cpu className="h-5 w-5" />
          <div>
            <p className="font-[family-name:var(--font-display)] text-sm uppercase tracking-[0.3em]">
              Mission Input
            </p>
            <p className="mt-1 text-sm text-slate-400">
              Describe the complex task you want the three agents to tackle.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-cyan-100" htmlFor="instruction">
          Task instruction
        </label>
        <textarea
          id="instruction"
          value={instruction}
          onChange={(event) => setInstruction(event.target.value)}
          rows={7}
          className="panel-glow w-full rounded-[1.75rem] border border-cyan-400/20 bg-slate-950/80 px-5 py-4 text-base text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-300 focus:ring-2 focus:ring-cyan-400/20"
          placeholder="Describe the business, strategy, technical research, or planning problem you want the agents to solve."
          required
          minLength={10}
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-cyan-100" htmlFor="context">
          Additional context
        </label>
        <textarea
          id="context"
          value={context}
          onChange={(event) => setContext(event.target.value)}
          rows={4}
          className="panel-glow w-full rounded-[1.75rem] border border-cyan-400/20 bg-slate-950/80 px-5 py-4 text-base text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-300 focus:ring-2 focus:ring-cyan-400/20"
          placeholder="Optional business context, constraints, or evaluation criteria."
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-cyan-100" htmlFor="reportTitle">
          Report title
        </label>
        <input
          id="reportTitle"
          type="text"
          value={reportTitle}
          onChange={(event) => setReportTitle(event.target.value)}
          className="panel-glow w-full rounded-[1.75rem] border border-cyan-400/20 bg-slate-950/80 px-5 py-4 text-base text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-300 focus:ring-2 focus:ring-cyan-400/20"
          placeholder="Optional title for the generated report"
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="inline-flex items-center justify-center gap-2 rounded-full border border-cyan-300/30 bg-cyan-400/15 px-6 py-3 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/25 disabled:cursor-not-allowed disabled:opacity-60"
      >
        <Sparkles className={`h-4 w-4 ${isSubmitting ? "animate-pulse" : ""}`} />
        {isSubmitting ? "Agents in progress..." : "Execute AgentOrchestrator"}
      </button>
    </form>
  );
}
