from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import httpx

from openevals_runner.executor import execute_suite_run
from openevals_runner.junit import build_junit_xml
from openevals_runner.parser import parse_suite_yaml


def _write_file(path: str | None, contents: str) -> None:
    if not path:
        return
    Path(path).write_text(contents, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openevals")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run an eval suite")
    run_parser.add_argument("suite_path", help="Path to a YAML eval suite")
    run_parser.add_argument("--model", action="append", dest="models", required=True)
    run_parser.add_argument("--api-key", dest="api_key")
    run_parser.add_argument("--judge-model", default=os.getenv("OPENEVALS_OPENAI_JUDGE_MODEL", "gpt-4.1-mini"))
    run_parser.add_argument("--output", help="Where to write JSON results")
    run_parser.add_argument("--junit", help="Where to write JUnit XML")
    run_parser.add_argument("--upload-url", help="Optional OpenEvals upload endpoint")
    run_parser.add_argument("--api-token", help="Deployment API token for uploads")
    run_parser.add_argument("--git-ref", default=os.getenv("GITHUB_REF_NAME"))
    run_parser.add_argument("--git-sha", default=os.getenv("GITHUB_SHA"))
    return parser


def run_command(args: argparse.Namespace) -> int:
    api_key = args.api_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPENEVALS_OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY or --api-key is required.")

    yaml_content = Path(args.suite_path).read_text(encoding="utf-8")
    parsed = parse_suite_yaml(yaml_content)
    result = execute_suite_run(
        suite=parsed.suite,
        models=args.models,
        judge_model=args.judge_model,
        api_key=api_key,
    )
    payload = {
        "suite_name": parsed.suite.name,
        "suite_hash": parsed.content_hash,
        "suite_yaml": parsed.canonical_yaml,
        "models": args.models,
        "git_ref": args.git_ref,
        "git_sha": args.git_sha,
        "result": result.model_dump(mode="json"),
    }
    json_output = json.dumps(payload, indent=2)
    _write_file(args.output, json_output)
    _write_file(args.junit, build_junit_xml(result, parsed.suite.name))

    if args.upload_url:
        headers = {"Content-Type": "application/json"}
        if args.api_token:
            headers["X-API-Token"] = args.api_token
        response = httpx.post(args.upload_url, headers=headers, content=json_output, timeout=30.0)
        response.raise_for_status()

    print(json_output)
    return 0 if result.status != "failed" else 1


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "run":
        return run_command(args)
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
