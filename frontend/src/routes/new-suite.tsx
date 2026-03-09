import CodeMirror from "@uiw/react-codemirror";
import { yaml as yamlLanguage } from "@codemirror/lang-yaml";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { useDeferredValue, useMemo, useState, startTransition } from "react";
import YAML from "yaml";

import { SectionCard } from "../components/SectionCard";
import { api } from "../lib/api";
import { starterSuite } from "../lib/starterSuite";

function extractVariables(yamlContent: string) {
  const matches = yamlContent.match(/\{\{\s*([a-zA-Z_][\w.]*)\s*\}\}/g) ?? [];
  return [...new Set(matches.map((value) => value.replace(/[{} ]/g, "")))];
}

export function NewSuiteRoute() {
  const navigate = useNavigate();
  const [yamlContent, setYamlContent] = useState(starterSuite);
  const [githubUrl, setGithubUrl] = useState("");
  const deferredYaml = useDeferredValue(yamlContent);
  const variables = useMemo(() => extractVariables(deferredYaml), [deferredYaml]);

  const importMutation = useMutation({
    mutationFn: api.importSuite,
    onSuccess: (suite) => {
      startTransition(() => {
        navigate({ to: "/suites/$suiteId", params: { suiteId: suite.id } });
      });
    },
  });

  const parsedPreview = useMemo(() => {
    try {
      const parsed = YAML.parse(deferredYaml) as { name?: string; cases?: Array<unknown> } | null;
      return {
        name: parsed?.name ?? "Untitled suite",
        cases: parsed?.cases?.length ?? 0,
      };
    } catch {
      return null;
    }
  }, [deferredYaml]);

  return (
    <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
      <SectionCard className="space-y-6">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Start here</p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight">Create or import a public-friendly eval suite</h2>
        </div>

        <div className="space-y-3 rounded-[1.5rem] bg-paper p-4">
          <label className="block text-sm font-medium">Import from GitHub URL</label>
          <input
            value={githubUrl}
            onChange={(event) => setGithubUrl(event.target.value)}
            placeholder="https://github.com/org/repo/blob/main/examples/suite.yaml"
            className="w-full rounded-2xl border border-ink/10 bg-white px-4 py-3 text-sm outline-none"
          />
          <button
            onClick={() => importMutation.mutate({ github_url: githubUrl })}
            disabled={!githubUrl || importMutation.isPending}
            className="rounded-full bg-spruce px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            Import from GitHub
          </button>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-[1.5rem] border border-ink/10 bg-white p-4">
            <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink/55">Variables</p>
            <p className="mt-2 text-2xl font-bold">{variables.length}</p>
          </div>
          <div className="rounded-[1.5rem] border border-ink/10 bg-white p-4">
            <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink/55">Cases</p>
            <p className="mt-2 text-2xl font-bold">{parsedPreview?.cases ?? "--"}</p>
          </div>
        </div>

        <div className="rounded-[1.5rem] bg-ink p-5 text-white">
          <p className="font-mono text-xs uppercase tracking-[0.22em] text-white/60">Why this structure works in public</p>
          <ul className="mt-4 space-y-2 text-sm text-white/80">
            <li>Readable YAML that diffs well in pull requests.</li>
            <li>Examples are easy to fork into benchmark repos.</li>
            <li>The same suite file runs in the UI and in GitHub Actions.</li>
          </ul>
        </div>
      </SectionCard>

      <SectionCard>
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.22em] text-ink/55">Suite YAML</p>
            <h3 className="mt-2 text-2xl font-bold tracking-tight">{parsedPreview?.name ?? "Draft suite"}</h3>
          </div>
          <button
            onClick={() => importMutation.mutate({ yaml_content: yamlContent })}
            disabled={importMutation.isPending}
            className="rounded-full bg-ember px-5 py-3 font-medium text-white disabled:opacity-50"
          >
            Save suite
          </button>
        </div>
        <div className="mt-6 overflow-hidden rounded-[1.5rem] border border-ink/10">
          <CodeMirror
            value={yamlContent}
            height="720px"
            extensions={[yamlLanguage()]}
            onChange={setYamlContent}
            basicSetup={{
              lineNumbers: true,
              foldGutter: false,
            }}
          />
        </div>
        {importMutation.error ? <p className="mt-4 text-sm text-ember">{String(importMutation.error.message)}</p> : null}
      </SectionCard>
    </div>
  );
}

