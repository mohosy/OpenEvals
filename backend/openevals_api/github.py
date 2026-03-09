from __future__ import annotations

from urllib.parse import urlparse

import httpx

from openevals_api.config import get_settings


def github_url_to_raw(url: str) -> str:
    if "raw.githubusercontent.com" in url:
        return url
    parsed = urlparse(url)
    if parsed.netloc != "github.com":
        return url
    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 5 and parts[2] == "blob":
        owner, repo, _, branch, *rest = parts
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{'/'.join(rest)}"
    return url


async def fetch_yaml_from_github(url: str) -> str:
    raw_url = github_url_to_raw(url)
    async with httpx.AsyncClient(timeout=get_settings().github_timeout_seconds) as client:
        response = await client.get(raw_url)
        response.raise_for_status()
        return response.text


def build_workflow_yaml(suite_path: str, upload_url: str | None = None) -> str:
    command_lines = [
        f"openevals run {suite_path} \\",
        "  --model gpt-4o \\",
        "  --model gpt-4.1 \\",
        "  --output openevals-results.json \\",
        "  --junit openevals-junit.xml \\",
    ]
    if upload_url:
        command_lines.extend(
            [
                f"  --upload-url {upload_url} \\",
                "  --api-token ${{ secrets.OPENEVALS_API_TOKEN }} \\",
            ]
        )
    command_lines[-1] = command_lines[-1].rstrip(" \\")
    command_block = "\n".join(f"          {line}" for line in command_lines)

    return f"""name: OpenEvals

on:
  pull_request:
  push:
    branches: [main]

jobs:
  evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install OpenEvals runner
        run: |
          python -m pip install --upgrade pip
          pip install ./backend
      - name: Run eval suite
        env:
          OPENAI_API_KEY: ${{{{ secrets.OPENAI_API_KEY }}}}
        run: |
{command_block}
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: openevals-results
          path: |
            openevals-results.json
            openevals-junit.xml
"""
