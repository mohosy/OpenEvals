from __future__ import annotations

from typing import Iterable, Optional

from openevals_runner.assertions import average_assertion_score, evaluate_assertion
from openevals_runner.openai_client import OpenAIService, ProviderUnavailableError
from openevals_runner.scoring import weighted_average
from openevals_runner.suite_models import (
    AssertionRule,
    CaseExecution,
    JudgeCriterion,
    PromptTemplate,
    RunExecutionResult,
    SuiteCase,
    SuiteDefinition,
    VariantExecution,
)
from openevals_runner.templates import render_template


def estimate_run_tokens(
    suite: SuiteDefinition,
    models: list[str],
    prompt_override: PromptTemplate | None = None,
    case_ids: Optional[set[str]] = None,
) -> int:
    prompt = prompt_override or suite.prompt
    selected_cases = [case for case in suite.cases if case_ids is None or case.id in case_ids]
    total_chars = 0
    for case in selected_cases:
        rendered_system = render_template(prompt.system, case.inputs) or ""
        rendered_user = render_template(prompt.user, case.inputs) or ""
        total_chars += len(rendered_system) + len(rendered_user)
    approximate_prompt_tokens = max(total_chars // 4, 1)
    return approximate_prompt_tokens * max(len(models), 1)


def _merge_judge_criteria(suite: SuiteDefinition, case: SuiteCase) -> list[JudgeCriterion]:
    return [*suite.judge, *case.judge]


def _materialize_expected(value: object, inputs: dict[str, object]) -> object:
    if isinstance(value, str):
        return render_template(value, inputs)
    if isinstance(value, list):
        return [_materialize_expected(item, inputs) for item in value]
    if isinstance(value, dict):
        return {key: _materialize_expected(item, inputs) for key, item in value.items()}
    return value


def _materialize_assertions(assertions: list[AssertionRule], inputs: dict[str, object]) -> list[AssertionRule]:
    materialized: list[AssertionRule] = []
    for assertion in assertions:
        materialized.append(
            AssertionRule(
                id=assertion.id,
                type=assertion.type,
                expected=_materialize_expected(assertion.expected, inputs),
                flags=assertion.flags,
            )
        )
    return materialized


def execute_suite_run(
    suite: SuiteDefinition,
    models: list[str],
    judge_model: str,
    api_key: str,
    prompt_override: PromptTemplate | None = None,
    case_ids: Optional[list[str]] = None,
) -> RunExecutionResult:
    selected_ids = set(case_ids or [])
    selected_cases = [case for case in suite.cases if not selected_ids or case.id in selected_ids]
    prompt_template = prompt_override or suite.prompt
    service = OpenAIService(api_key=api_key, judge_model=judge_model)

    cases: list[CaseExecution] = []
    provider_errors = 0
    for position, case in enumerate(selected_cases):
        rendered_prompt = PromptTemplate(
            system=render_template(prompt_template.system, case.inputs),
            user=render_template(prompt_template.user, case.inputs) or "",
        )
        variants: list[VariantExecution] = []
        merged_assertions = _materialize_assertions([*suite.assertions, *case.assertions], case.inputs)
        merged_judge = _merge_judge_criteria(suite, case)

        for variant_index, model in enumerate(models):
            try:
                output = service.generate(model=model, prompt=rendered_prompt)
                assertion_outcomes = [evaluate_assertion(rule, output) for rule in merged_assertions]
                judge_outcomes = [
                    service.judge(
                        criterion=criterion,
                        rendered_prompt=rendered_prompt,
                        output=output,
                        model_name=model,
                    )
                    for criterion in merged_judge
                ]
                weighted_scores = [(item.score, 1.0) for item in assertion_outcomes]
                weighted_scores.extend(
                    (item.score, criterion.weight)
                    for item, criterion in zip(judge_outcomes, merged_judge)
                )
                variant_score = weighted_average(weighted_scores)
                variants.append(
                    VariantExecution(
                        label="A" if variant_index == 0 else "B",
                        model=model,
                        rendered_prompt=rendered_prompt.model_dump(),
                        output=output,
                        status="completed",
                        score=variant_score,
                        assertions=assertion_outcomes,
                        judgments=judge_outcomes,
                    )
                )
            except ProviderUnavailableError as exc:
                provider_errors += 1
                variants.append(
                    VariantExecution(
                        label="A" if variant_index == 0 else "B",
                        model=model,
                        rendered_prompt=rendered_prompt.model_dump(),
                        status="error",
                        error_message=str(exc),
                    )
                )

        successful_scores = [item.score for item in variants if item.status == "completed" and item.score is not None]
        case_status = "completed" if successful_scores else "error"
        cases.append(
            CaseExecution(
                case_id=case.id,
                description=case.description,
                position=position,
                inputs=case.inputs,
                status=case_status,
                score=sum(successful_scores) / len(successful_scores) if successful_scores else None,
                variants=variants,
                error_message=None if successful_scores else "All variants failed for this case.",
            )
        )

    completed_cases = len([case for case in cases if case.status == "completed"])
    failed_cases = len(cases) - completed_cases
    run_scores = [case.score for case in cases if case.score is not None]
    status = "completed"
    if completed_cases == 0 and cases:
        status = "failed"
    elif failed_cases > 0:
        status = "partial"
    if provider_errors == len(selected_cases) * max(len(models), 1) and cases:
        status = "failed"

    return RunExecutionResult(
        status=status,
        score=(sum(run_scores) / len(run_scores) * 100) if run_scores else 0.0,
        total_cases=len(cases),
        completed_cases=completed_cases,
        failed_cases=failed_cases,
        token_estimate=estimate_run_tokens(
            suite=suite,
            models=models,
            prompt_override=prompt_override,
            case_ids=selected_ids or None,
        ),
        cases=cases,
    )
