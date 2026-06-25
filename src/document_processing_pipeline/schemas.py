from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from document_processing_pipeline.domain import DocumentStatus, JobStatus


class HealthResponse(BaseModel):
    status: str


class IngestDocumentRequest(BaseModel):
    filename: str = Field(min_length=1)
    content: str = Field(min_length=1)
    mime_type: str = "text/plain"
    metadata: dict[str, str] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    content: str
    mime_type: str
    metadata: dict[str, str]
    status: DocumentStatus
    classification: str | None
    redacted_content: str | None
    created_at: datetime
    updated_at: datetime


class ExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    text: str
    fields: dict[str, str]
    entities: dict[str, list[str]]
    created_at: datetime


class ProcessingJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    status: JobStatus
    steps: list[str]
    error: str | None
    created_at: datetime
    updated_at: datetime
