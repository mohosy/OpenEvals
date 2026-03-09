from __future__ import annotations

import json
from typing import Optional

from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI, RateLimitError

from openevals_runner.scoring import normalize_judge_score
from openevals_runner.suite_models import JudgeCriterion, JudgeOutcome, PromptTemplate


class ProviderUnavailableError(RuntimeError):
    """Raised when OpenAI is unavailable or rejects the request."""


def _extract_text(message_content: object) -> str:
    if isinstance(message_content, str):
        return message_content
    if isinstance(message_content, list):
        parts = []
        for item in message_content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "\n".join(parts)
    return str(message_content)


class OpenAIService:
    def __init__(self, api_key: str, judge_model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.judge_model = judge_model

    def generate(self, model: str, prompt: PromptTemplate) -> str:
        try:
            messages = []
            if prompt.system:
                messages.append({"role": "system", "content": prompt.system})
            messages.append({"role": "user", "content": prompt.user})
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            return _extract_text(response.choices[0].message.content).strip()
        except (APIConnectionError, APIStatusError, AuthenticationError, RateLimitError) as exc:
            raise ProviderUnavailableError(str(exc)) from exc

    def judge(
        self,
        criterion: JudgeCriterion,
        rendered_prompt: PromptTemplate,
        output: str,
        model_name: str,
    ) -> JudgeOutcome:
        system_message = (
            "You are an evaluation judge. Score the candidate response from 1 to 5, "
            "where 1 is poor and 5 is excellent. Return valid JSON with keys "
            "'score' and 'reason'."
        )
        user_message = json.dumps(
            {
                "rubric_name": criterion.name,
                "rubric": criterion.rubric,
                "model_under_test": model_name,
                "prompt": {
                    "system": rendered_prompt.system,
                    "user": rendered_prompt.user,
                },
                "candidate_output": output,
            },
            indent=2,
        )
        try:
            response = self.client.chat.completions.create(
                model=self.judge_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
            parsed = json.loads(_extract_text(response.choices[0].message.content))
        except (APIConnectionError, APIStatusError, AuthenticationError, RateLimitError) as exc:
            raise ProviderUnavailableError(str(exc)) from exc

        score_raw = int(parsed.get("score", 1))
        return JudgeOutcome(
            id=criterion.id or criterion.name,
            name=criterion.name,
            score_raw=score_raw,
            score=normalize_judge_score(score_raw),
            reason=str(parsed.get("reason", "")).strip(),
        )

