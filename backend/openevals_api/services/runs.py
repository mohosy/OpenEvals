from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from openevals_api.config import get_settings
from openevals_api.database import SessionLocal
from openevals_api.models import Run, RunCaseResult, Suite
from openevals_api.security import decrypt_secret
from openevals_api.services.core import compare_case_scores, serialize_run, utcnow
from openevals_runner.executor import execute_suite_run
from openevals_runner.parser import parse_suite_yaml
from openevals_runner.suite_models import PromptTemplate, RunExecutionResult


def persist_execution_result(session: Session, run: Run, result: RunExecutionResult) -> Run:
    run.status = result.status
    run.score = result.score
    run.token_estimate = result.token_estimate
    run.summary_json = {
        **(run.summary_json or {}),
        "total_cases": result.total_cases,
        "completed_cases": result.completed_cases,
        "failed_cases": result.failed_cases,
    }
    run.case_results.clear()
    for case in result.cases:
        run.case_results.append(
            RunCaseResult(
                run_id=run.id,
                case_id=case.case_id,
                position=case.position,
                status=case.status,
                score=case.score,
                inputs_json=case.inputs,
                variants_json=[item.model_dump(mode="json") for item in case.variants],
                error_message=case.error_message,
            )
        )

    suite = session.get(Suite, run.suite_id)
    baseline_run = session.get(Run, suite.baseline_run_id) if suite and suite.baseline_run_id else None
    delta, improved, unchanged, regressed = compare_case_scores(run, baseline_run)
    run.baseline_delta = delta
    run.improved_cases = improved
    run.unchanged_cases = unchanged
    run.regressed_cases = regressed
    run.completed_at = utcnow()
    run.api_key_ciphertext = None
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def process_run_by_id(run_id: str) -> dict[str, Any]:
    settings = get_settings()
    with SessionLocal() as session:
        run = session.get(Run, run_id)
        if run is None:
            raise ValueError(f"Run {run_id} was not found.")
        parsed = parse_suite_yaml(run.suite_version.yaml_content)
        api_key = decrypt_secret(run.api_key_ciphertext) or settings.openai_api_key
        if not api_key:
            run.status = "failed"
            run.error_message = "No OpenAI API key configured."
            run.completed_at = utcnow()
            session.add(run)
            session.commit()
            session.refresh(run)
            return serialize_run(run)
        run.status = "running"
        run.started_at = utcnow()
        session.add(run)
        session.commit()
        session.refresh(run)
        result = execute_suite_run(
            suite=parsed.suite,
            models=[item for item in [run.primary_model, run.secondary_model] if item],
            judge_model=settings.openai_judge_model,
            api_key=api_key,
            prompt_override=PromptTemplate.model_validate(run.draft_prompt_override) if run.draft_prompt_override else None,
            case_ids=run.selected_case_ids,
        )
        persisted = persist_execution_result(session, run, result)
        return serialize_run(persisted)
