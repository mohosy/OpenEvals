import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, BookOpen, Sparkles } from "lucide-react";

import { SectionCard } from "../components/SectionCard";
import { StatusPill } from "../components/StatusPill";
import { api } from "../lib/api";
import { formatDelta, formatScore } from "../lib/utils";

export function HomeRoute() {
  const suitesQuery = useQuery({
    queryKey: ["suites"],
    queryFn: api.listSuites,
  });

  const suites = suitesQuery.data ?? [];

  return (
    <div className="space-y-8">
      <SectionCard className="overflow-hidden">
        <div className="grid gap-10 lg:grid-cols-[1.25fr_0.85fr]">
          <div className="space-y-6">
            <p className="font-mono text-xs uppercase tracking-[0.3em] text-ink/55">Run prompt evals like a product team</p>
            <div className="space-y-4">
              <h2 className="max-w-3xl text-5xl font-bold tracking-tight text-ink">
                Compare prompts and models side by side, then ship only when the regression score moves up.
              </h2>
              <p className="max-w-2xl text-lg leading-8 text-ink/70">
                OpenEvals is an open-source studio for Git-tracked eval suites, baseline pinning, and GitHub-native CI.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link
                to="/suites/new"
                className="inline-flex items-center gap-2 rounded-full bg-ember px-5 py-3 font-medium text-white"
              >
                Create a suite
                <ArrowRight className="h-4 w-4" />
              </Link>
              <a
                href="https://github.com"
                className="inline-flex items-center gap-2 rounded-full border border-ink/10 bg-white px-5 py-3 font-medium"
                rel="noreferrer"
                target="_blank"
              >
                <Sparkles className="h-4 w-4 text-ember" />
                Launch this publicly
              </a>
            </div>
          </div>
          <div className="rounded-[2rem] bg-ink p-6 text-white">
            <p className="font-mono text-xs uppercase tracking-[0.24em] text-white/60">Public-ready starter pack</p>
            <ul className="mt-6 space-y-4 text-sm text-white/80">
              <li className="rounded-2xl border border-white/10 bg-white/5 p-4">GitHub Action generator with JSON and JUnit artifacts</li>
              <li className="rounded-2xl border border-white/10 bg-white/5 p-4">Suite YAML that versions cleanly in public repos</li>
              <li className="rounded-2xl border border-white/10 bg-white/5 p-4">A side-by-side compare screen that looks good in screenshots</li>
            </ul>
          </div>
        </div>
      </SectionCard>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <SectionCard>
          <div className="flex items-start justify-between">
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Examples</p>
              <h3 className="mt-2 text-2xl font-bold tracking-tight">Benchmarks people can fork</h3>
            </div>
            <BookOpen className="h-5 w-5 text-ember" />
          </div>
          <div className="mt-6 space-y-4">
            {[
              "Support ticket routing",
              "Structured extraction",
              "Summarization clarity",
            ].map((example) => (
              <div key={example} className="rounded-[1.5rem] border border-ink/10 bg-paper p-4">
                <p className="text-base font-semibold">{example}</p>
                <p className="mt-1 text-sm text-ink/60">Designed to be screenshot-friendly, Git-friendly, and useful immediately.</p>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Workspace</p>
              <h3 className="mt-2 text-2xl font-bold tracking-tight">Suites in this deployment</h3>
            </div>
            {suitesQuery.isLoading ? <StatusPill status="pending" /> : <StatusPill status="completed" />}
          </div>
          <div className="mt-6 space-y-4">
            {suites.length === 0 ? (
              <div className="rounded-[1.5rem] border border-dashed border-ink/15 bg-paper p-8 text-center">
                <p className="text-lg font-semibold">No suites yet</p>
                <p className="mt-2 text-sm text-ink/60">Import YAML from GitHub or start from the built-in starter template.</p>
              </div>
            ) : (
              suites.map((suite) => {
                const latestRun = suite.recent_runs[0];
                return (
                  <Link
                    key={suite.id}
                    to="/suites/$suiteId"
                    params={{ suiteId: suite.id }}
                    className="block rounded-[1.5rem] border border-ink/10 bg-paper p-5 transition hover:-translate-y-1"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <p className="text-lg font-semibold">{suite.name}</p>
                        <p className="mt-1 text-sm text-ink/60">{suite.description ?? "No description yet."}</p>
                      </div>
                      <StatusPill status={latestRun?.status ?? "pending"} />
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {suite.tags.map((tag) => (
                        <span key={tag} className="rounded-full bg-white px-3 py-1 font-mono text-xs uppercase tracking-[0.14em] text-ink/60">
                          {tag}
                        </span>
                      ))}
                    </div>
                    <div className="mt-5 grid gap-3 sm:grid-cols-2">
                      <div className="rounded-2xl bg-white p-4">
                        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink/55">Latest score</p>
                        <p className="mt-2 text-2xl font-bold">{formatScore(latestRun?.score)}</p>
                      </div>
                      <div className="rounded-2xl bg-white p-4">
                        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink/55">Baseline delta</p>
                        <p className="mt-2 text-2xl font-bold">{formatDelta(latestRun?.baseline_delta)}</p>
                      </div>
                    </div>
                  </Link>
                );
              })
            )}
          </div>
        </SectionCard>
      </div>
    </div>
  );
}

