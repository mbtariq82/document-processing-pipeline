from __future__ import annotations

from document_processing_pipeline.extraction import ExtractionService
from document_processing_pipeline.ingestion import IngestionService
from document_processing_pipeline.processing import ProcessingService
from document_processing_pipeline.repository import DocumentRepository


def test_processing_job_classifies_redacts_and_updates_status() -> None:
    repository = DocumentRepository()
    ingestion = IngestionService(repository)
    extraction = ExtractionService(repository)
    processing = ProcessingService(repository, extraction)
    document = ingestion.ingest(
        "invoice-001.txt",
        "\n".join(
            [
                "Invoice Number: INV-001",
                "Total: 1200.50",
                "Contact: finance@example.com",
            ]
        ),
    )

    job = processing.process(document.id)
    processed = repository.get_document(document.id)

    assert job.status == "completed"
    assert job.steps == ["extracted_text", "classified_document", "redacted_pii"]
    assert processed.status == "processed"
    assert processed.classification == "invoice"
    assert processed.redacted_content is not None
    assert "finance@example.com" not in processed.redacted_content
    assert "[redacted-email]" in processed.redacted_content
