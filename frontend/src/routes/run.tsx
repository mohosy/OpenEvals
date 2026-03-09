import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "@tanstack/react-router";
import { BarChart3, GitCompare, Pin } from "lucide-react";

import { MetricCard } from "../components/MetricCard";
import { SectionCard } from "../components/SectionCard";
import { StatusPill } from "../components/StatusPill";
import { api } from "../lib/api";
import { formatDelta, formatScore } from "../lib/utils";

export function RunRoute() {
  const { runId } = useParams({ from: "/runs/$runId" });
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const runQuery = useQuery({
    queryKey: ["run", runId],
    queryFn: () => api.getRun(runId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "pending" || status === "running" ? 2000 : false;
    },
  });

  const setBaselineMutation = useMutation({
    mutationFn: () => api.setBaseline(runId),
    onSuccess: (payload) => {
      queryClient.invalidateQueries({ queryKey: ["suite", payload.suite_id] });
      queryClient.invalidateQueries({ queryKey: ["suites"] });
      queryClient.invalidateQueries({ queryKey: ["run", runId] });
    },
  });

  const run = runQuery.data;
  if (!run) {
    return <SectionCard>{runQuery.isLoading ? "Loading run..." : "Run not found."}</SectionCard>;
  }

  return (
    <div className="space-y-6">
      <SectionCard>
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Compare view</p>
            <h2 className="mt-2 text-4xl font-bold tracking-tight">{run.models.join(" vs ")}</h2>
            <p className="mt-3 max-w-2xl text-lg text-ink/70">
              Review deterministic checks, judge outputs, and per-case regressions against the pinned baseline.
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate({ to: "/suites/$suiteId", params: { suiteId: run.suite_id } })}
              className="rounded-full border border-ink/10 bg-white px-4 py-3 text-sm font-medium"
            >
              Back to suite
            </button>
            <button
              onClick={() => setBaselineMutation.mutate()}
              className="inline-flex items-center gap-2 rounded-full bg-spruce px-4 py-3 text-sm font-medium text-white"
            >
              <Pin className="h-4 w-4" />
              Pin as baseline
            </button>
          </div>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-5">
          <MetricCard label="Run score" value={formatScore(run.score)} />
          <MetricCard label="Regression" value={formatDelta(run.baseline_delta)} />
          <MetricCard label="Improved" value={`${run.improved_cases}`} />
          <MetricCard label="Unchanged" value={`${run.unchanged_cases}`} />
          <MetricCard label="Regressed" value={`${run.regressed_cases}`} />
        </div>
      </SectionCard>

      <div className="grid gap-6 lg:grid-cols-[0.32fr_1fr]">
        <SectionCard className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Status</p>
              <h3 className="mt-2 text-2xl font-bold tracking-tight">Run telemetry</h3>
            </div>
            <StatusPill status={run.status} />
          </div>
          <div className="rounded-[1.5rem] bg-paper p-4">
            <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink/55">Token estimate</p>
            <p className="mt-2 text-2xl font-bold">{run.token_estimate}</p>
          </div>
          <div className="rounded-[1.5rem] bg-paper p-4">
            <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink/55">Case health</p>
            <p className="mt-2 text-sm text-ink/65">
              {String(run.summary?.completed_cases ?? 0)} complete / {String(run.summary?.failed_cases ?? 0)} failed
            </p>
          </div>
          <div className="rounded-[1.5rem] bg-ink p-4 text-white">
            <div className="inline-flex items-center gap-2 text-sm font-medium">
              <BarChart3 className="h-4 w-4 text-ember" />
              Shareable view
            </div>
            <p className="mt-3 text-sm text-white/75">
              This compare layout is designed to screenshot cleanly for GitHub READMEs, tweets, and launch posts.
            </p>
          </div>
        </SectionCard>

        <div className="space-y-6">
          {run.cases.map((item) => (
            <SectionCard key={item.case_id}>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Case {item.position + 1}</p>
                  <h3 className="mt-2 text-2xl font-bold tracking-tight">{item.case_id}</h3>
                  <p className="mt-2 text-sm text-ink/65">Inputs: {JSON.stringify(item.inputs)}</p>
                </div>
                <div className="text-right">
                  <StatusPill status={item.status} />
                  <p className="mt-3 text-sm text-ink/60">
                    Score {formatScore(item.score)} • Delta {formatDelta(item.delta)}
                  </p>
                </div>
              </div>

              <div className={`mt-6 grid gap-4 ${item.variants.length > 1 ? "md:grid-cols-2" : "md:grid-cols-1"}`}>
                {item.variants.map((variant) => (
                  <div key={`${item.case_id}-${variant.label}`} className="rounded-[1.5rem] border border-ink/10 bg-paper p-5">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Variant {variant.label}</p>
                        <h4 className="mt-2 text-xl font-bold tracking-tight">{variant.model}</h4>
                      </div>
                      <div className="text-right">
                        <StatusPill status={variant.status} />
                        <p className="mt-2 text-sm text-ink/60">Score {formatScore(variant.score)}</p>
                      </div>
                    </div>
                    <div className="mt-5 space-y-4">
                      <div className="rounded-2xl bg-white p-4">
                        <div className="flex items-center gap-2 text-sm font-medium">
                          <GitCompare className="h-4 w-4 text-spruce" />
                          Output
                        </div>
                        <pre className="mt-3 whitespace-pre-wrap text-sm text-ink/75">{variant.output ?? variant.error_message}</pre>
                      </div>
                      <div className="grid gap-3 lg:grid-cols-2">
                        <div className="rounded-2xl bg-white p-4">
                          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink/55">Assertions</p>
                          <ul className="mt-3 space-y-2 text-sm text-ink/70">
                            {variant.assertions.length === 0 ? (
                              <li>No deterministic checks</li>
                            ) : (
                              variant.assertions.map((assertion) => (
                                <li key={assertion.id}>
                                  {assertion.id}: {assertion.passed ? "pass" : "fail"}
                                </li>
                              ))
                            )}
                          </ul>
                        </div>
                        <div className="rounded-2xl bg-white p-4">
                          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink/55">Judge notes</p>
                          <ul className="mt-3 space-y-3 text-sm text-ink/70">
                            {variant.judgments.length === 0 ? (
                              <li>No rubric checks</li>
                            ) : (
                              variant.judgments.map((judgment) => (
                                <li key={judgment.id}>
                                  <strong>{judgment.name}</strong>: {judgment.score_raw}/5
                                  <p className="mt-1 text-ink/55">{judgment.reason}</p>
                                </li>
                              ))
                            )}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>
          ))}
        </div>
      </div>
    </div>
  );
}
