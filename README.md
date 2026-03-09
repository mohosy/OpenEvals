# OpenEvals

[![CI](https://github.com/mohosy/OpenEvals/actions/workflows/ci.yml/badge.svg)](https://github.com/mohosy/OpenEvals/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-black.svg)](./LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/mohosy/OpenEvals?style=social)](https://github.com/mohosy/OpenEvals/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/mohosy/OpenEvals?style=social)](https://github.com/mohosy/OpenEvals/network/members)

![OpenEvals social preview](./docs/openevals-social.png)

OpenEvals is an open-source React + FastAPI studio for running prompt evals, comparing models side by side, pinning a baseline, and shipping the same suite in GitHub Actions.

If you build with the OpenAI API and want a free, visual alternative to CLI-only eval workflows, this is for you.

> Star the repo if you want open-source prompt eval tooling to become a category, not a side project.

It is designed for public OSS adoption:

- Beautiful compare screens that are screenshot-friendly
- Git-tracked YAML suites that fork cleanly
- OpenAI-first runner for `gpt-4o`, `gpt-4.1`, and `gpt-4.1-mini`
- Regression deltas against a pinned baseline
- Generated GitHub Actions workflow plus a reusable `openevals` CLI

## Why people share it

- The eval suite format is readable enough to post in a tweet, gist, or blog post.
- The compare view is designed to look good in screenshots and release notes.
- Benchmarks are forkable: contributors can publish suites for support, extraction, summarization, and more.
- The same suite runs in the web UI and in CI, so examples are not toy demos.

## Community

- Share ideas or show what you built in [GitHub Discussions](https://github.com/mohosy/OpenEvals/discussions)
- Browse starter benchmarks in [examples/suites](./examples/suites/README.md)
- Open feature requests or benchmark requests in [Issues](https://github.com/mohosy/OpenEvals/issues)
- Read the launch plan in [docs/launch-playbook.md](./docs/launch-playbook.md)

## Stack

- Frontend: React, TypeScript, Vite, TanStack Router, TanStack Query, Tailwind, Radix, CodeMirror
- Backend: FastAPI, Pydantic v2, SQLAlchemy, PostgreSQL, Redis, Dramatiq
- Runner: shared Python package used by the API and CLI

## Quickstart

1. Copy `.env.example` to `.env`.
2. Start infrastructure:

   ```bash
   docker compose up postgres redis
   ```

3. Install dependencies:

   ```bash
   make setup
   ```

4. Run the app:

   ```bash
   make backend
   make worker
   make frontend
   ```

5. Open [http://localhost:5173](http://localhost:5173).

## What works today

- Create a suite from starter YAML or import one from GitHub
- Save versioned suite revisions in the backend
- Run one or two OpenAI models against a suite
- Compare per-case outputs, assertions, and judge notes
- Pin a run as the baseline and inspect regression counts
- Export the suite YAML and a GitHub Actions workflow
- Upload CI results back into the app with an API token

## Benchmarks wanted

OpenEvals gets more useful as more teams share realistic suites. High-value contributions:

- Classification and routing evals
- JSON extraction and schema adherence suites
- Summarization and rewrite quality benchmarks
- RAG answer-quality evals
- Customer support, sales, and internal tooling prompts

## Repo layout

- `frontend/`: React app
- `backend/openevals_api`: FastAPI app and worker wiring
- `backend/openevals_runner`: shared runner and CLI
- `examples/suites/`: public example eval suites

## Share your suite

1. Copy one of the suites in [`examples/suites`](./examples/suites/README.md).
2. Adapt the prompt, inputs, and assertions to your domain.
3. Publish the YAML in your repo and link it in [GitHub Discussions](https://github.com/mohosy/OpenEvals/discussions).
4. If it is broadly useful, open a benchmark contribution issue or pull request.

## CLI

Run a suite locally:

```bash
cd backend
uv run openevals run ../examples/suites/support-routing.yaml \
  --model gpt-4o \
  --model gpt-4.1 \
  --output openevals-results.json \
  --junit openevals-junit.xml
```

## Making this public

- MIT licensed
- `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, issue templates, and CI included
- `SECURITY.md` and `SUPPORT.md` included for a complete GitHub community profile
- Launch checklist in [docs/launch-playbook.md](./docs/launch-playbook.md)

## Status

This is an MVP scaffold aimed at the first public release. The core product loop is in place, but production hardening, auth, and a hosted suite gallery are intentionally out of scope for `v0.1`.
