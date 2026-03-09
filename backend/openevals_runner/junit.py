from __future__ import annotations

import xml.etree.ElementTree as ET

from openevals_runner.suite_models import RunExecutionResult


def build_junit_xml(result: RunExecutionResult, suite_name: str) -> str:
    testsuite = ET.Element(
        "testsuite",
        name=suite_name,
        tests=str(result.total_cases),
        failures=str(result.failed_cases),
    )
    for case in result.cases:
        testcase = ET.SubElement(
            testsuite,
            "testcase",
            classname=suite_name,
            name=case.case_id,
        )
        if case.status == "error":
            failure = ET.SubElement(testcase, "failure", message=case.error_message or "Case failed")
            failure.text = case.error_message or "All variants failed."
    return ET.tostring(testsuite, encoding="unicode")

