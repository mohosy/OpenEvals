export type PromptTemplate = {
  system?: string | null;
  user: string;
};

export type Variant = {
  label: string;
  model: string;
  rendered_prompt: PromptTemplate;
  output?: string | null;
  status: "completed" | "error";
  score?: number | null;
  assertions: Array<{
    id: string;
    type: string;
    passed: boolean;
    score: number;
    message: string;
  }>;
  judgments: Array<{
    id: string;
    name: string;
    score_raw: number;
    score: number;
    reason: string;
  }>;
  error_message?: string | null;
};

export type RunCase = {
  case_id: string;
  position: number;
  status: "completed" | "error";
  score?: number | null;
  baseline_score?: number | null;
  delta?: number | null;
  inputs: Record<string, unknown>;
  variants: Variant[];
  error_message?: string | null;
};

export type Run = {
  id: string;
  status: string;
  suite_id: string;
  suite_version_id: string;
  models: string[];
  score?: number | null;
  baseline_delta?: number | null;
  improved_cases: number;
  unchanged_cases: number;
  regressed_cases: number;
  token_estimate: number;
  error_message?: string | null;
  source: string;
  summary?: Record<string, unknown> | null;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  cases: RunCase[];
};

export type Suite = {
  id: string;
  slug: string;
  name: string;
  description?: string | null;
  tags: string[];
  baseline_run_id?: string | null;
  created_at: string;
  updated_at: string;
  latest_version_hash?: string | null;
  yaml_content?: string | null;
  parsed_suite?: Record<string, unknown> | null;
  variables: string[];
  recent_runs: Run[];
};

