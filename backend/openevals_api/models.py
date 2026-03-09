from __future__ import annotations

import uuid

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from openevals_api.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Suite(Base):
    __tablename__ = "suites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    baseline_run_id: Mapped[str | None] = mapped_column(ForeignKey("runs.id"), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    versions: Mapped[list["SuiteVersion"]] = relationship(
        back_populates="suite",
        cascade="all, delete-orphan",
        foreign_keys="SuiteVersion.suite_id",
        order_by="desc(SuiteVersion.created_at)",
    )
    runs: Mapped[list["Run"]] = relationship(
        back_populates="suite",
        cascade="all, delete-orphan",
        foreign_keys="Run.suite_id",
    )
    baseline_run: Mapped["Run | None"] = relationship(foreign_keys=[baseline_run_id], post_update=True)


class SuiteVersion(Base):
    __tablename__ = "suite_versions"
    __table_args__ = (UniqueConstraint("suite_id", "content_hash", name="uq_suite_content_hash"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    suite_id: Mapped[str] = mapped_column(ForeignKey("suites.id"), index=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    yaml_content: Mapped[str] = mapped_column(Text)
    parsed_json: Mapped[dict] = mapped_column(JSON)
    variable_names: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    suite: Mapped["Suite"] = relationship(back_populates="versions", foreign_keys=[suite_id])
    runs: Mapped[list["Run"]] = relationship(back_populates="suite_version")


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    suite_id: Mapped[str] = mapped_column(ForeignKey("suites.id"), index=True)
    suite_version_id: Mapped[str] = mapped_column(ForeignKey("suite_versions.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    primary_model: Mapped[str] = mapped_column(String(128))
    secondary_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    draft_prompt_override: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    selected_case_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    api_key_ciphertext: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    baseline_delta: Mapped[float | None] = mapped_column(Float, nullable=True)
    improved_cases: Mapped[int] = mapped_column(Integer, default=0)
    unchanged_cases: Mapped[int] = mapped_column(Integer, default=0)
    regressed_cases: Mapped[int] = mapped_column(Integer, default=0)
    token_estimate: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="app")
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)

    suite: Mapped["Suite"] = relationship(back_populates="runs", foreign_keys=[suite_id])
    suite_version: Mapped["SuiteVersion"] = relationship(back_populates="runs")
    case_results: Mapped[list["RunCaseResult"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="RunCaseResult.position",
    )


class RunCaseResult(Base):
    __tablename__ = "run_case_results"
    __table_args__ = (UniqueConstraint("run_id", "case_id", name="uq_run_case"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    case_id: Mapped[str] = mapped_column(String(255), index=True)
    position: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32))
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    baseline_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    delta: Mapped[float | None] = mapped_column(Float, nullable=True)
    inputs_json: Mapped[dict] = mapped_column(JSON, default=dict)
    variants_json: Mapped[list[dict]] = mapped_column(JSON, default=list)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run: Mapped["Run"] = relationship(back_populates="case_results")

