from __future__ import annotations

from document_processing_pipeline.domain import Document, ValidationError
from document_processing_pipeline.repository import DocumentRepository


class IngestionService:
    def __init__(self, repository: DocumentRepository) -> None:
        self.repository = repository

    def ingest(
        self,
        filename: str,
        content: str,
        mime_type: str = "text/plain",
        metadata: dict[str, str] | None = None,
    ) -> Document:
        if not filename.strip():
            raise ValidationError("filename is required.")
        if not content.strip():
            raise ValidationError("content is required.")
        if mime_type not in {"text/plain", "application/pdf", "application/msword"}:
            raise ValidationError("Unsupported mime_type.")
        return self.repository.save_document(
            Document(
                filename=filename.strip(),
                content=content,
                mime_type=mime_type,
                metadata=metadata or {},
            )
        )
