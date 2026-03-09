from __future__ import annotations

import hashlib
from dataclasses import dataclass

import yaml

from openevals_runner.suite_models import SuiteDefinition
from openevals_runner.templates import ensure_variables_present, extract_variables


@dataclass
class ParsedSuite:
    suite: SuiteDefinition
    content_hash: str
    canonical_yaml: str
    variables: list[str]


def parse_suite_yaml(yaml_content: str) -> ParsedSuite:
    data = yaml.safe_load(yaml_content)
    suite = SuiteDefinition.model_validate(data)
    variables = extract_variables(suite.prompt.system, suite.prompt.user)
    for case in suite.cases:
        ensure_variables_present(variables, case.inputs)
    canonical_yaml = yaml.safe_dump(
        suite.model_dump(mode="json", exclude_none=True),
        sort_keys=False,
        allow_unicode=False,
    )
    content_hash = hashlib.sha256(canonical_yaml.encode("utf-8")).hexdigest()
    return ParsedSuite(
        suite=suite,
        content_hash=content_hash,
        canonical_yaml=canonical_yaml,
        variables=variables,
    )

