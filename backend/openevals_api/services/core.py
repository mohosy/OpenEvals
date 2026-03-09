from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from openevals_api.models import Run, RunCaseResult, Suite, SuiteVersion


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "suite"


def latest_version_for_suite(session: Session, suite_id: str) -> SuiteVersion | None:
    return session.scalar(
        select(SuiteVersion).where(SuiteVersion.suite_id == suite_id).order_by(SuiteVersion.created_at.desc())
    )


def serialize_run(run: Run) -> dict[str, Any]:
    return {
        "id": run.id,
        "status": run.status,
        "suite_id": run.suite_id,
        "suite_version_id": run.suite_version_id,
        "models": [item for item in [run.primary_model, run.secondary_model] if item],
        "score": run.score,
        "baseline_delta": run.baseline_delta,
        "improved_cases": run.improved_cases,
        "unchanged_cases": run.unchanged_cases,
        "regressed_cases": run.regressed_cases,
        "token_estimate": run.token_estimate,
        "error_message": run.error_message,
        "source": run.source,
        "summary": run.summary_json,
        "created_at": run.created_at,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "cases": [
            {
                "case_id": item.case_id,
                "position": item.position,
                "status": item.status,
                "score": item.score,
                "baseline_score": item.baseline_score,
                "delta": item.delta,
                "inputs": item.inputs_json,
                "variants": item.variants_json,
                "error_message": item.error_message,
            }
            for item in sorted(run.case_results, key=lambda value: value.position)
        ],
    }


def serialize_suite(session: Session, suite: Suite) -> dict[str, Any]:
    latest_version = latest_version_for_suite(session, suite.id)
    recent_runs = session.scalars(
        select(Run).where(Run.suite_id == suite.id).order_by(Run.created_at.desc()).limit(8)
    ).all()
    return {
        "id": suite.id,
        "slug": suite.slug,
        "name": suite.name,
        "description": suite.description,
        "tags": suite.tags or [],
        "baseline_run_id": suite.baseline_run_id,
        "created_at": suite.created_at,
        "updated_at": suite.updated_at,
        "latest_version_hash": latest_version.content_hash if latest_version else None,
        "yaml_content": latest_version.yaml_content if latest_version else None,
        "parsed_suite": latest_version.parsed_json if latest_version else None,
        "variables": latest_version.variable_names if latest_version else [],
        "recent_runs": [serialize_run(run) for run in recent_runs],
    }


def compare_case_scores(run: Run, baseline: Run | None) -> tuple[float | None, int, int, int]:
    if baseline is None:
        return None, 0, 0, 0
    baseline_map = {item.case_id: item for item in baseline.case_results}
    improved = 0
    unchanged = 0
    regressed = 0
    deltas: list[float] = []
    for case in run.case_results:
        baseline_case = baseline_map.get(case.case_id)
        if baseline_case is None or case.score is None or baseline_case.score is None:
            continue
        delta = case.score - baseline_case.score
        case.baseline_score = baseline_case.score
        case.delta = delta
        deltas.append(delta)
        if delta > 0.001:
            improved += 1
        elif delta < -0.001:
            regressed += 1
        else:
            unchanged += 1
    if run.score is not None and baseline.score is not None:
        overall_delta = run.score - baseline.score
    else:
        overall_delta = None
    return overall_delta, improved, unchanged, regressed

