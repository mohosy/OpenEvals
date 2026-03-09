from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from openevals_api.config import get_settings
from openevals_api.database import get_db, init_db
from openevals_api.github import build_workflow_yaml, fetch_yaml_from_github
from openevals_api.models import Run, Suite, SuiteVersion
from openevals_api.schemas import CiRunUploadRequest, RunCreateRequest, SuiteImportRequest, SuiteUpdateRequest
from openevals_api.security import encrypt_secret, require_api_token
from openevals_api.services.core import latest_version_for_suite, serialize_run, serialize_suite, slugify, utcnow
from openevals_api.services.runs import persist_execution_result
from openevals_runner.executor import estimate_run_tokens
from openevals_runner.parser import parse_suite_yaml
from openevals_runner.suite_models import RunExecutionResult

app = FastAPI(title="OpenEvals")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/suites")
def list_suites(db: Session = Depends(get_db)) -> list[dict]:
    suites = db.scalars(select(Suite).order_by(Suite.updated_at.desc())).all()
    return [serialize_suite(db, suite) for suite in suites]


@app.post("/api/suites/import", status_code=status.HTTP_201_CREATED)
async def import_suite(request: SuiteImportRequest, db: Session = Depends(get_db)) -> dict:
    yaml_content = request.yaml_content
    if request.github_url:
        yaml_content = await fetch_yaml_from_github(request.github_url)
    if not yaml_content:
        raise HTTPException(status_code=400, detail="Provide yaml_content or github_url.")
    parsed = parse_suite_yaml(yaml_content)
    suite_slug = request.slug or slugify(parsed.suite.name)
    suite = db.scalar(select(Suite).where(Suite.slug == suite_slug))
    if suite is None:
        suite = Suite(
            slug=suite_slug,
            name=parsed.suite.name,
            description=parsed.suite.description,
            tags=parsed.suite.tags,
        )
        db.add(suite)
        db.flush()
    else:
        suite.name = parsed.suite.name
        suite.description = parsed.suite.description
        suite.tags = parsed.suite.tags

    version = db.scalar(
        select(SuiteVersion).where(
            SuiteVersion.suite_id == suite.id,
            SuiteVersion.content_hash == parsed.content_hash,
        )
    )
    if version is None:
        version = SuiteVersion(
            suite_id=suite.id,
            content_hash=parsed.content_hash,
            yaml_content=parsed.canonical_yaml,
            parsed_json=parsed.suite.model_dump(mode="json"),
            variable_names=parsed.variables,
        )
        db.add(version)
    db.commit()
    db.refresh(suite)
    return serialize_suite(db, suite)


@app.put("/api/suites/{suite_id}")
def update_suite(suite_id: str, request: SuiteUpdateRequest, db: Session = Depends(get_db)) -> dict:
    suite = db.get(Suite, suite_id)
    if suite is None:
        raise HTTPException(status_code=404, detail="Suite not found.")
    parsed = parse_suite_yaml(request.yaml_content)
    suite.slug = request.slug or suite.slug
    suite.name = parsed.suite.name
    suite.description = parsed.suite.description
    suite.tags = parsed.suite.tags
    version = db.scalar(
        select(SuiteVersion).where(
            SuiteVersion.suite_id == suite.id,
            SuiteVersion.content_hash == parsed.content_hash,
        )
    )
    if version is None:
        db.add(
            SuiteVersion(
                suite_id=suite.id,
                content_hash=parsed.content_hash,
                yaml_content=parsed.canonical_yaml,
                parsed_json=parsed.suite.model_dump(mode="json"),
                variable_names=parsed.variables,
            )
        )
    db.commit()
    db.refresh(suite)
    return serialize_suite(db, suite)


@app.get("/api/suites/{suite_id}")
def get_suite(suite_id: str, db: Session = Depends(get_db)) -> dict:
    suite = db.get(Suite, suite_id)
    if suite is None:
        raise HTTPException(status_code=404, detail="Suite not found.")
    return serialize_suite(db, suite)


@app.post("/api/suites/{suite_id}/runs", status_code=status.HTTP_201_CREATED)
def create_run(suite_id: str, request: RunCreateRequest, db: Session = Depends(get_db)) -> dict:
    suite = db.get(Suite, suite_id)
    if suite is None:
        raise HTTPException(status_code=404, detail="Suite not found.")
    latest_version = latest_version_for_suite(db, suite.id)
    if latest_version is None:
        raise HTTPException(status_code=400, detail="Suite has no versions.")
    parsed = parse_suite_yaml(latest_version.yaml_content)
    models = request.models or parsed.suite.models or ["gpt-4o"]
    if not 1 <= len(models) <= 2:
        raise HTTPException(status_code=400, detail="Provide one or two models.")
    run = Run(
        suite_id=suite.id,
        suite_version_id=latest_version.id,
        status="pending",
        primary_model=models[0],
        secondary_model=models[1] if len(models) > 1 else None,
        draft_prompt_override=request.prompt_override.model_dump(mode="json") if request.prompt_override else None,
        selected_case_ids=request.case_ids,
        api_key_ciphertext=encrypt_secret(request.api_key_override),
        token_estimate=estimate_run_tokens(
            suite=parsed.suite,
            models=models,
            prompt_override=request.prompt_override,
            case_ids=set(request.case_ids or []),
        ),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    from openevals_api.worker import enqueue_run

    enqueue_run(run.id)
    db.refresh(run)
    return serialize_run(run)


@app.get("/api/runs/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db)) -> dict:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return serialize_run(run)


@app.get("/api/runs/{run_id}/compare/{other_run_id}")
def compare_runs(run_id: str, other_run_id: str, db: Session = Depends(get_db)) -> dict:
    left = db.get(Run, run_id)
    right = db.get(Run, other_run_id)
    if left is None or right is None:
        raise HTTPException(status_code=404, detail="One or both runs were not found.")
    right_cases = {item.case_id: item for item in right.case_results}
    case_diffs = []
    for case in left.case_results:
        other = right_cases.get(case.case_id)
        case_diffs.append(
            {
                "case_id": case.case_id,
                "left_score": case.score,
                "right_score": other.score if other else None,
                "delta": (case.score - other.score) if other and case.score is not None and other.score is not None else None,
                "left_variants": case.variants_json,
                "right_variants": other.variants_json if other else [],
            }
        )
    return {
        "left": serialize_run(left),
        "right": serialize_run(right),
        "cases": case_diffs,
    }


@app.post("/api/runs/{run_id}/set-baseline")
def set_baseline(run_id: str, db: Session = Depends(get_db)) -> dict:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    suite = db.get(Suite, run.suite_id)
    suite.baseline_run_id = run.id
    db.commit()
    db.refresh(suite)
    return {"suite_id": suite.id, "baseline_run_id": suite.baseline_run_id}


@app.post("/api/ci/runs/upload", dependencies=[Depends(require_api_token)], status_code=status.HTTP_201_CREATED)
def upload_ci_run(payload: CiRunUploadRequest, db: Session = Depends(get_db)) -> dict:
    parsed = parse_suite_yaml(payload.suite_yaml)
    suite_slug = slugify(payload.suite_name)
    suite = db.scalar(select(Suite).where(Suite.slug == suite_slug))
    if suite is None:
        suite = Suite(
            slug=suite_slug,
            name=parsed.suite.name,
            description=parsed.suite.description,
            tags=parsed.suite.tags,
        )
        db.add(suite)
        db.flush()
    version = db.scalar(
        select(SuiteVersion).where(
            SuiteVersion.suite_id == suite.id,
            SuiteVersion.content_hash == payload.suite_hash,
        )
    )
    if version is None:
        version = SuiteVersion(
            suite_id=suite.id,
            content_hash=payload.suite_hash,
            yaml_content=parsed.canonical_yaml,
            parsed_json=parsed.suite.model_dump(mode="json"),
            variable_names=parsed.variables,
        )
        db.add(version)
        db.flush()
    result = payload.result
    run = Run(
        suite_id=suite.id,
        suite_version_id=version.id,
        status=result.get("status", "completed"),
        primary_model=payload.models[0],
        secondary_model=payload.models[1] if len(payload.models) > 1 else None,
        score=result.get("score"),
        token_estimate=result.get("token_estimate", 0),
        source="github_actions",
        started_at=utcnow(),
        completed_at=utcnow(),
        summary_json={
            "git_ref": payload.git_ref,
            "git_sha": payload.git_sha,
        },
    )
    db.add(run)
    db.flush()
    execution = RunExecutionResult.model_validate(result)
    return serialize_run(persist_execution_result(db, run, execution))


@app.get("/api/integrations/github/workflow")
def github_workflow(
    suite_path: str = Query(...),
    upload_url: str | None = Query(default=None),
) -> Response:
    return Response(
        content=build_workflow_yaml(suite_path=suite_path, upload_url=upload_url),
        media_type="text/plain",
    )


def main() -> None:
    import uvicorn

    uvicorn.run("openevals_api.main:app", host="0.0.0.0", port=8000, reload=True)
