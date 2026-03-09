FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml README.md ./
COPY openevals_api ./openevals_api
COPY openevals_runner ./openevals_runner

RUN uv pip install --system .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "openevals_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

