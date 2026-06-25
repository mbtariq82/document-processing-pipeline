from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class DocumentError(Exception):
    pass


class NotFoundError(DocumentError):
    pass


class ValidationError(DocumentError):
    pass


class DocumentStatus(StrEnum):
    INGESTED = "ingested"
    PROCESSED = "processed"
    FAILED = "failed"


class JobStatus(StrEnum):
    QUEUED = "queued"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Document:
    filename: str
    content: str
    mime_type: str
    metadata: dict[str, str]
    status: DocumentStatus = DocumentStatus.INGESTED
    classification: str | None = None
    redacted_content: str | None = None
    id: str = field(default_factory=lambda: new_id("doc"))
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class ExtractionResult:
    document_id: str
    text: str
    fields: dict[str, str]
    entities: dict[str, list[str]]
    id: str = field(default_factory=lambda: new_id("extract"))
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class ProcessingJob:
    document_id: str
    status: JobStatus = JobStatus.QUEUED
    steps: list[str] = field(default_factory=list)
    error: str | None = None
    id: str = field(default_factory=lambda: new_id("job"))
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
