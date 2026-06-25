from __future__ import annotations

from threading import RLock

from document_processing_pipeline.domain import (
    Document,
    ExtractionResult,
    NotFoundError,
    ProcessingJob,
)


class DocumentRepository:
    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}
        self._extractions: dict[str, ExtractionResult] = {}
        self._jobs: dict[str, ProcessingJob] = {}
        self._lock = RLock()

    def save_document(self, document: Document) -> Document:
        with self._lock:
            self._documents[document.id] = document
            return document

    def get_document(self, document_id: str) -> Document:
        with self._lock:
            try:
                return self._documents[document_id]
            except KeyError as exc:
                raise NotFoundError(f"Document {document_id!r} was not found.") from exc

    def list_documents(self) -> list[Document]:
        with self._lock:
            return list(self._documents.values())

    def save_extraction(self, result: ExtractionResult) -> ExtractionResult:
        with self._lock:
            self._extractions[result.document_id] = result
            return result

    def get_extraction(self, document_id: str) -> ExtractionResult:
        with self._lock:
            try:
                return self._extractions[document_id]
            except KeyError as exc:
                raise NotFoundError(f"Extraction for document {document_id!r} was not found.") from exc

    def save_job(self, job: ProcessingJob) -> ProcessingJob:
        with self._lock:
            self._jobs[job.id] = job
            return job

    def get_job(self, job_id: str) -> ProcessingJob:
        with self._lock:
            try:
                return self._jobs[job_id]
            except KeyError as exc:
                raise NotFoundError(f"Job {job_id!r} was not found.") from exc
