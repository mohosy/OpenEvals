import CodeMirror from "@uiw/react-codemirror";
import { yaml as yamlLanguage } from "@codemirror/lang-yaml";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "@tanstack/react-router";
import { Download, GitBranch, Play, RefreshCcw } from "lucide-react";
import { startTransition, useMemo, useState } from "react";

import { MetricCard } from "../components/MetricCard";
import { SectionCard } from "../components/SectionCard";
import { StatusPill } from "../components/StatusPill";
import { api } from "../lib/api";
import { downloadTextFile, formatDelta, formatScore } from "../lib/utils";

const modelOptions = ["gpt-4o", "gpt-4.1", "gpt-4.1-mini"];

export function SuiteRoute() {
  const { suiteId } = useParams({ from: "/suites/$suiteId" });
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const suiteQuery = useQuery({
    queryKey: ["suite", suiteId],
    queryFn: () => api.getSuite(suiteId),
  });
  const suite = suiteQuery.data;
  const [yamlContent, setYamlContent] = useState("");
  const [apiKeyOverride, setApiKeyOverride] = useState("");
  const [primaryModel, setPrimaryModel] = useState("gpt-4o");
  const [secondaryModel, setSecondaryModel] = useState("gpt-4.1");
  const [draftSystem, setDraftSystem] = useState("");
  const [draftUser, setDraftUser] = useState("");

  const effectiveYaml = yamlContent || suite?.yaml_content || "";
  const tokenEstimate = useMemo(() => {
    if (!suite?.parsed_suite) {
      return "--";
    }
    const cases = Array.isArray((suite.parsed_suite as { cases?: unknown[] }).cases)
      ? ((suite.parsed_suite as { cases?: unknown[] }).cases?.length ?? 0)
      : 0;
    const totalChars = effectiveYaml.length;
    return `${Math.max(Math.floor(totalChars / 4) * (secondaryModel ? 2 : 1) * Math.max(cases, 1), 1)}`;
  }, [effectiveYaml, secondaryModel, suite?.parsed_suite]);

  const saveMutation = useMutation({
    mutationFn: (payload: { yaml_content: string }) => api.updateSuite(suiteId, payload),
    onSuccess: (updated) => {
      setYamlContent(updated.yaml_content ?? "");
      queryClient.setQueryData(["suite", suiteId], updated);
      queryClient.invalidateQueries({ queryKey: ["suites"] });
    },
  });

  const runMutation = useMutation({
    mutationFn: () =>
      api.createRun(suiteId, {
        models: secondaryModel ? [primaryModel, secondaryModel] : [primaryModel],
        api_key_override: apiKeyOverride || null,
        prompt_override:
          draftSystem || draftUser
            ? {
                system: draftSystem || undefined,
                user: draftUser || String((suite?.parsed_suite as { prompt?: { user?: string } })?.prompt?.user ?? ""),
              }
            : null,
      }),
    onSuccess: (run) => {
      startTransition(() => {
        navigate({ to: "/runs/$runId", params: { runId: run.id } });
      });
    },
  });

  if (!suite) {
    return <SectionCard>{suiteQuery.isLoading ? "Loading suite..." : "Suite not found."}</SectionCard>;
  }

  const latestRun = suite.recent_runs[0];
  const defaultPrompt = (suite.parsed_suite as { prompt?: { system?: string; user?: string } })?.prompt;

  return (
    <div className="space-y-6">
      <SectionCard>
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Suite editor</p>
            <h2 className="mt-2 text-4xl font-bold tracking-tight">{suite.name}</h2>
            <p className="mt-3 max-w-3xl text-lg text-ink/70">{suite.description ?? "No description yet."}</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={async () => {
                const workflow = await api.getWorkflow(`examples/suites/${suite.slug}.yaml`);
                downloadTextFile(`${suite.slug}.yaml`, effectiveYaml);
                downloadTextFile("openevals.yml", workflow);
              }}
              className="inline-flex items-center gap-2 rounded-full border border-ink/10 bg-white px-4 py-3 text-sm font-medium"
            >
              <Download className="h-4 w-4" />
              Export
            </button>
            <button
              onClick={() => saveMutation.mutate({ yaml_content: effectiveYaml })}
              className="inline-flex items-center gap-2 rounded-full bg-ink px-4 py-3 text-sm font-medium text-white"
            >
              <RefreshCcw className="h-4 w-4" />
              Save revision
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <MetricCard label="Variables" value={`${suite.variables.length}`} />
          <MetricCard label="Latest score" value={formatScore(latestRun?.score)} />
          <MetricCard label="Baseline delta" value={formatDelta(latestRun?.baseline_delta)} />
          <MetricCard label="Token estimate" value={tokenEstimate} hint="Rough prompt-token approximation" />
        </div>
      </SectionCard>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <SectionCard>
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Canonical YAML</p>
              <h3 className="mt-2 text-2xl font-bold tracking-tight">Git-ready suite definition</h3>
            </div>
            {saveMutation.isPending ? <StatusPill status="running" /> : <StatusPill status="completed" />}
          </div>
          <div className="mt-6 overflow-hidden rounded-[1.5rem] border border-ink/10">
            <CodeMirror
              value={effectiveYaml}
              height="760px"
              extensions={[yamlLanguage()]}
              onChange={setYamlContent}
            />
          </div>
        </SectionCard>

        <div className="space-y-6">
          <SectionCard>
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Launch a run</p>
            <h3 className="mt-2 text-2xl font-bold tracking-tight">Model compare or prompt compare</h3>
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <label className="space-y-2 text-sm">
                <span className="font-medium">Primary model</span>
                <select
                  value={primaryModel}
                  onChange={(event) => setPrimaryModel(event.target.value)}
                  className="w-full rounded-2xl border border-ink/10 bg-paper px-4 py-3"
                >
                  {modelOptions.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </label>
              <label className="space-y-2 text-sm">
                <span className="font-medium">Secondary model</span>
                <select
                  value={secondaryModel}
                  onChange={(event) => setSecondaryModel(event.target.value)}
                  className="w-full rounded-2xl border border-ink/10 bg-paper px-4 py-3"
                >
                  <option value="">No compare</option>
                  {modelOptions.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <label className="mt-4 block space-y-2 text-sm">
              <span className="font-medium">Per-session API key override</span>
              <input
                type="password"
                value={apiKeyOverride}
                onChange={(event) => setApiKeyOverride(event.target.value)}
                placeholder="Uses server OPENAI_API_KEY when left empty"
                className="w-full rounded-2xl border border-ink/10 bg-paper px-4 py-3"
              />
            </label>
            <div className="mt-5 rounded-[1.5rem] bg-paper p-4">
              <div className="flex items-center gap-2 text-sm font-medium">
                <GitBranch className="h-4 w-4 text-spruce" />
                Draft prompt override
              </div>
              <textarea
                rows={5}
                value={draftSystem}
                onChange={(event) => setDraftSystem(event.target.value)}
                placeholder={defaultPrompt?.system ?? "Optional system override"}
                className="mt-3 w-full rounded-2xl border border-ink/10 bg-white px-4 py-3 text-sm"
              />
              <textarea
                rows={8}
                value={draftUser}
                onChange={(event) => setDraftUser(event.target.value)}
                placeholder={defaultPrompt?.user ?? "Optional user prompt override"}
                className="mt-3 w-full rounded-2xl border border-ink/10 bg-white px-4 py-3 text-sm"
              />
            </div>
            <button
              onClick={() => runMutation.mutate()}
              disabled={runMutation.isPending}
              className="mt-5 inline-flex items-center gap-2 rounded-full bg-ember px-5 py-3 font-medium text-white disabled:opacity-50"
            >
              <Play className="h-4 w-4" />
              Run eval
            </button>
            {runMutation.error ? <p className="mt-3 text-sm text-ember">{String(runMutation.error.message)}</p> : null}
          </SectionCard>

          <SectionCard>
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Recent runs</p>
            <div className="mt-5 space-y-3">
              {suite.recent_runs.map((run) => (
                <button
                  key={run.id}
                  onClick={() => navigate({ to: "/runs/$runId", params: { runId: run.id } })}
                  className="flex w-full items-center justify-between rounded-[1.5rem] border border-ink/10 bg-paper p-4 text-left"
                >
                  <div>
                    <p className="font-medium">{run.models.join(" vs ")}</p>
                    <p className="mt-1 text-sm text-ink/60">Score {formatScore(run.score)} • Delta {formatDelta(run.baseline_delta)}</p>
                  </div>
                  <StatusPill status={run.status} />
                </button>
              ))}
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
