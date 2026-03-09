from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


AssertionType = Literal["exact_match", "contains", "regex", "json_schema"]
VariantStatus = Literal["completed", "error"]
RunStatus = Literal["completed", "partial", "failed"]


class PromptTemplate(BaseModel):
    system: Optional[str] = None
    user: str


class AssertionRule(BaseModel):
    id: Optional[str] = None
    type: AssertionType
    expected: Any
    flags: List[str] = Field(default_factory=list)


class JudgeCriterion(BaseModel):
    id: Optional[str] = None
    name: str
    rubric: str
    weight: float = 1.0


class SuiteCase(BaseModel):
    id: str
    description: Optional[str] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    assertions: List[AssertionRule] = Field(default_factory=list)
    judge: List[JudgeCriterion] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class SuiteDefinition(BaseModel):
    version: str
    name: str
    description: Optional[str] = None
    models: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    prompt: PromptTemplate
    assertions: List[AssertionRule] = Field(default_factory=list)
    judge: List[JudgeCriterion] = Field(default_factory=list)
    cases: List[SuiteCase]

    @model_validator(mode="after")
    def ensure_cases(self) -> "SuiteDefinition":
        if not self.cases:
            raise ValueError("Suites must define at least one case.")
        return self


class AssertionOutcome(BaseModel):
    id: str
    type: AssertionType
    passed: bool
    score: float
    message: str


class JudgeOutcome(BaseModel):
    id: str
    name: str
    score_raw: int
    score: float
    reason: str


class VariantExecution(BaseModel):
    label: str
    model: str
    rendered_prompt: Dict[str, Optional[str]]
    output: Optional[str] = None
    status: VariantStatus
    score: Optional[float] = None
    assertions: List[AssertionOutcome] = Field(default_factory=list)
    judgments: List[JudgeOutcome] = Field(default_factory=list)
    error_message: Optional[str] = None


class CaseExecution(BaseModel):
    case_id: str
    description: Optional[str] = None
    position: int
    inputs: Dict[str, Any]
    status: Literal["completed", "error"]
    score: Optional[float] = None
    variants: List[VariantExecution]
    error_message: Optional[str] = None


class RunExecutionResult(BaseModel):
    status: RunStatus
    score: float
    total_cases: int
    completed_cases: int
    failed_cases: int
    token_estimate: int
    cases: List[CaseExecution]

