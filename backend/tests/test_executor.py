from openevals_runner.executor import execute_suite_run
from openevals_runner.parser import parse_suite_yaml


def test_execute_suite_run_renders_assertion_templates(monkeypatch) -> None:
    parsed = parse_suite_yaml(
        """
version: "0.1"
name: Route tickets
prompt:
  user: "Ticket {{ticket}}"
assertions:
  - id: queue-match
    type: contains
    expected: '"queue": "{{expected_queue}}"'
cases:
  - id: security
    inputs:
      ticket: suspicious login
      expected_queue: security
"""
    )

    class FakeService:
        def __init__(self, api_key: str, judge_model: str) -> None:
            self.api_key = api_key
            self.judge_model = judge_model

        def generate(self, model: str, prompt):
            assert prompt.user == "Ticket suspicious login"
            return '{"queue": "security"}'

        def judge(self, criterion, rendered_prompt, output, model_name):
            raise AssertionError("Judge should not be called in this test")

    monkeypatch.setattr("openevals_runner.executor.OpenAIService", FakeService)

    result = execute_suite_run(
        suite=parsed.suite,
        models=["gpt-4o"],
        judge_model="gpt-4.1-mini",
        api_key="test-key",
    )

    assert result.status == "completed"
    assert result.score == 100.0
    assert result.cases[0].variants[0].assertions[0].passed is True

