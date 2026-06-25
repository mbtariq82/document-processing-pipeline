from __future__ import annotations

from fastapi.testclient import TestClient

from document_processing_pipeline.main import create_app


def test_api_ingests_extracts_processes_and_retrieves_document() -> None:
    client = TestClient(create_app())
    created = client.post(
        "/documents",
        json={
            "filename": "invoice-001.txt",
            "content": "\n".join(
                [
                    "Invoice Number: INV-001",
                    "Total: 1200.50",
                    "Contact: finance@example.com",
                ]
            ),
            "metadata": {"source": "upload"},
        },
    )
    assert created.status_code == 201
    document_id = created.json()["id"]

    extraction = client.post(f"/documents/{document_id}/extract")
    job = client.post(f"/documents/{document_id}/process")
    document = client.get(f"/documents/{document_id}")

    assert extraction.status_code == 200
    assert extraction.json()["fields"]["invoice_number"] == "INV-001"
    assert job.status_code == 200
    assert job.json()["status"] == "completed"
    assert document.json()["status"] == "processed"
    assert document.json()["classification"] == "invoice"
    assert "finance@example.com" not in document.json()["redacted_content"]
