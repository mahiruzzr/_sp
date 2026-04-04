import { Bot, CheckCircle2, CircleDashed, LoaderCircle, TriangleAlert } from "lucide-react";

import type { AgentStageSnapshot } from "@/lib/types";

type StatusListProps = {
  stages: AgentStageSnapshot[];
  progressMessage: string;
  currentAgent: string | null;
  isBusy: boolean;
};

const statusStyles = {
  pending: {
    icon: CircleDashed,
    iconClassName: "text-slate-500",
    badgeClassName: "border-slate-700 bg-slate-900/80 text-slate-400",
  },
  running: {
    icon: LoaderCircle,
    iconClassName: "animate-spin text-cyan-300",
    badgeClassName: "border-cyan-400/30 bg-cyan-500/10 text-cyan-200",
  },
  completed: {
    icon: CheckCircle2,
    iconClassName: "text-emerald-300",
    badgeClassName: "border-emerald-400/30 bg-emerald-500/10 text-emerald-200",
  },
  failed: {
    icon: TriangleAlert,
    iconClassName: "text-rose-300",
    badgeClassName: "border-rose-400/30 bg-rose-500/10 text-rose-200",
  },
} as const;

export function StatusList({ stages, progressMessage, currentAgent, isBusy }: StatusListProps) {
  return (
    <section className="panel-glow scanline rounded-[1.75rem] border border-cyan-400/20 bg-slate-950/70 p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-cyan-300/70">Execution Status</p>
          <h2 className="mt-3 font-[family-name:var(--font-display)] text-2xl text-white">
            Agent activity timeline
          </h2>
        </div>
        <div className="rounded-full border border-cyan-400/20 bg-cyan-500/10 px-3 py-1 text-xs uppercase tracking-[0.25em] text-cyan-200">
          {isBusy ? "Live" : "Idle"}
        </div>
      </div>

      <div className="mt-5 flex items-center gap-3 rounded-2xl border border-cyan-400/15 bg-slate-900/70 px-4 py-3 text-sm text-slate-300">
        <Bot className="h-4 w-4 text-cyan-300" />
        <span>{progressMessage}</span>
      </div>

      <div className="mt-6 space-y-4">
        {stages.map((stage) => {
          const style = statusStyles[stage.status];
          const Icon = style.icon;
          const isCurrent = currentAgent === stage.name && stage.status === "running";

          return (
            <div
              key={stage.name}
              className={`rounded-2xl border px-4 py-4 transition ${
                isCurrent
                  ? "border-cyan-300/40 bg-cyan-500/10 shadow-[0_0_24px_rgba(34,211,238,0.12)]"
                  : "border-slate-800 bg-slate-950/50"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-2">
                    <Icon className={`h-4 w-4 ${style.iconClassName}`} />
                  </div>
                  <div>
                    <div className="flex items-center gap-3">
                      <span className="font-[family-name:var(--font-display)] text-sm tracking-[0.25em] text-slate-200">
                        {stage.name}
                      </span>
                      <span className={`rounded-full border px-2 py-1 text-[10px] uppercase tracking-[0.25em] ${style.badgeClassName}`}>
                        {stage.status}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-slate-400">{stage.message}</p>
                  </div>
                </div>
                <span className="text-xs uppercase tracking-[0.25em] text-slate-500">0{stage.order}</span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
