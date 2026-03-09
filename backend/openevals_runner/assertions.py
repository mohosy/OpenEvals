from __future__ import annotations

import json
import re
from typing import Any

from jsonschema import ValidationError, validate

from openevals_runner.suite_models import AssertionOutcome, AssertionRule


def evaluate_assertion(assertion: AssertionRule, output: str) -> AssertionOutcome:
    identifier = assertion.id or assertion.type
    if assertion.type == "exact_match":
        passed = output.strip() == str(assertion.expected).strip()
        return AssertionOutcome(
            id=identifier,
            type=assertion.type,
            passed=passed,
            score=1.0 if passed else 0.0,
            message="Output exactly matched expected text." if passed else "Output did not exactly match expected text.",
        )

    if assertion.type == "contains":
        passed = str(assertion.expected) in output
        return AssertionOutcome(
            id=identifier,
            type=assertion.type,
            passed=passed,
            score=1.0 if passed else 0.0,
            message="Output contained expected text." if passed else "Output did not contain expected text.",
        )

    if assertion.type == "regex":
        flags = 0
        if "ignorecase" in assertion.flags:
            flags |= re.IGNORECASE
        passed = re.search(str(assertion.expected), output, flags=flags) is not None
        return AssertionOutcome(
            id=identifier,
            type=assertion.type,
            passed=passed,
            score=1.0 if passed else 0.0,
            message="Regex matched the output." if passed else "Regex did not match the output.",
        )

    if assertion.type == "json_schema":
        try:
            parsed = json.loads(output)
            validate(instance=parsed, schema=assertion.expected)
            return AssertionOutcome(
                id=identifier,
                type=assertion.type,
                passed=True,
                score=1.0,
                message="Output matched the expected JSON schema.",
            )
        except (json.JSONDecodeError, ValidationError) as exc:
            return AssertionOutcome(
                id=identifier,
                type=assertion.type,
                passed=False,
                score=0.0,
                message=f"JSON schema validation failed: {exc}",
            )

    raise ValueError(f"Unsupported assertion type: {assertion.type}")


def average_assertion_score(outcomes: list[AssertionOutcome]) -> float | None:
    if not outcomes:
        return None
    return sum(item.score for item in outcomes) / len(outcomes)

