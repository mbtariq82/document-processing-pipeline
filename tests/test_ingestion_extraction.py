from __future__ import annotations

from document_processing_pipeline.extraction import ExtractionService
from document_processing_pipeline.ingestion import IngestionService
from document_processing_pipeline.repository import DocumentRepository


def test_ingests_document_and_extracts_fields_and_entities() -> None:
    repository = DocumentRepository()
    ingestion = IngestionService(repository)
    extraction = ExtractionService(repository)
    document = ingestion.ingest(
        "invoice-001.txt",
        "\n".join(
            [
                "Invoice Number: INV-001",
                "Supplier: Example Ltd",
                "Total: 1200.50",
                "Contact: finance@example.com",
            ]
        ),
        metadata={"source": "upload"},
    )

    result = extraction.extract(document.id)

    assert document.status == "ingested"
    assert result.fields["invoice_number"] == "INV-001"
    assert result.fields["total"] == "1200.50"
    assert result.entities["emails"] == ["finance@example.com"]
    assert repository.get_extraction(document.id).id == result.id
