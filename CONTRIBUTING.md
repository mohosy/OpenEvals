# Contributing

Thanks for contributing to OpenEvals.

## Development

1. Copy `.env.example` to `.env`.
2. Run `make setup`.
3. Start infrastructure with `docker compose up postgres redis`.
4. In separate terminals run `make backend`, `make worker`, and `make frontend`.

## Workflow

- Open an issue before larger changes so roadmap work stays coordinated.
- Keep pull requests focused and include before/after screenshots for UI changes.
- Add or update tests for backend behavior and runner logic.
- Prefer YAML suite examples that demonstrate realistic eval patterns.
- If you contribute a public benchmark, make it safe to share and easy to fork.

## Benchmark Contributions

We want OpenEvals to develop a library of forkable eval suites.

Strong benchmark contributions usually:

- Cover a real production use case
- Use public-safe or synthetic inputs
- Include a short explanation of what success looks like
- Combine deterministic checks with one or two rubric criteria when needed
- Explain why the suite is useful outside one company

## Pull Request Checklist

- The app starts locally.
- Backend tests pass.
- `frontend` builds successfully.
- Docs or examples are updated for visible behavior changes.
