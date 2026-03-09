import { Suite, Run } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const payload = await response.text();
    throw new Error(payload || `Request failed with status ${response.status}`);
  }

  if (response.headers.get("content-type")?.includes("text/plain")) {
    return (await response.text()) as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  listSuites: () => request<Suite[]>("/api/suites"),
  getSuite: (suiteId: string) => request<Suite>(`/api/suites/${suiteId}`),
  importSuite: (payload: { yaml_content?: string; github_url?: string; slug?: string }) =>
    request<Suite>("/api/suites/import", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateSuite: (suiteId: string, payload: { yaml_content: string; slug?: string }) =>
    request<Suite>(`/api/suites/${suiteId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  createRun: (
    suiteId: string,
    payload: {
      models: string[];
      prompt_override?: { system?: string | null; user: string } | null;
      api_key_override?: string | null;
      case_ids?: string[] | null;
    },
  ) =>
    request<Run>(`/api/suites/${suiteId}/runs`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getRun: (runId: string) => request<Run>(`/api/runs/${runId}`),
  setBaseline: (runId: string) =>
    request<{ suite_id: string; baseline_run_id: string }>(`/api/runs/${runId}/set-baseline`, {
      method: "POST",
    }),
  getWorkflow: (suitePath: string, uploadUrl?: string) => {
    const searchParams = new URLSearchParams({ suite_path: suitePath });
    if (uploadUrl) {
      searchParams.set("upload_url", uploadUrl);
    }
    return request<string>(`/api/integrations/github/workflow?${searchParams.toString()}`);
  },
};

