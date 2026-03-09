SHELL := /bin/zsh

.PHONY: setup backend frontend worker test

setup:
	cd backend && uv sync
	cd frontend && npm install

backend:
	cd backend && uv run uvicorn openevals_api.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

worker:
	cd backend && uv run openevals-worker

test:
	cd backend && uv run pytest
	cd frontend && npm run build

