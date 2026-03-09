from openevals_runner.parser import parse_suite_yaml


def test_parse_suite_yaml_extracts_variables_and_normalizes() -> None:
    parsed = parse_suite_yaml(
        """
version: "0.1"
name: Example
prompt:
  system: "You are helpful."
  user: "Hello {{name}} from {{company}}"
cases:
  - id: hello
    inputs:
      name: Mo
      company: OpenEvals
"""
    )

    assert parsed.suite.name == "Example"
    assert parsed.variables == ["name", "company"]
    assert "Hello {{name}} from {{company}}" in parsed.canonical_yaml

