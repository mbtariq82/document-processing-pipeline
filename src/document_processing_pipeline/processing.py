from __future__ import annotations

import re

from document_processing_pipeline.domain import DocumentError, DocumentStatus, JobStatus, ProcessingJob, utcnow
from document_processing_pipeline.extraction import ExtractionService
from document_processing_pipeline.repository import DocumentRepository


class ProcessingService:
    EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

    def __init__(
        self,
        repository: DocumentRepository,
        extraction_service: ExtractionService,
    ) -> None:
        self.repository = repository
        self.extraction_service = extraction_service

    def process(self, document_id: str) -> ProcessingJob:
        document = self.repository.get_document(document_id)
        job = self.repository.save_job(ProcessingJob(document_id=document.id))
        try:
            extraction = self.extraction_service.extract(document.id)
            job.steps.append("extracted_text")
            document.classification = self._classify(extraction.text, extraction.fields)
            job.steps.append("classified_document")
            document.redacted_content = self.EMAIL_PATTERN.sub("[redacted-email]", document.content)
            job.steps.append("redacted_pii")
            document.status = DocumentStatus.PROCESSED
            document.updated_at = utcnow()
            job.status = JobStatus.COMPLETED
        except DocumentError as exc:
            document.status = DocumentStatus.FAILED
            job.status = JobStatus.FAILED
            job.error = str(exc)
        job.updated_at = utcnow()
        self.repository.save_document(document)
        return self.repository.save_job(job)

    @staticmethod
    def _classify(text: str, fields: dict[str, str]) -> str:
        normalized = text.lower()
        if "invoice" in normalized or "invoice_number" in fields or "total" in fields:
            return "invoice"
        if "agreement" in normalized or "contract" in normalized:
            return "contract"
        return "general"
