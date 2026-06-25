# Document Processing Pipeline

Training implementation of a document processing API. It supports document
ingestion, text and field extraction, simple entity detection, processing jobs,
classification, and PII redaction.

## Features

- Ingest text-like documents with metadata and validation.
- Extract key-value fields such as invoice numbers and totals.
- Detect email entities in document content.
- Run processing jobs that extract text, classify documents, redact email
  addresses, and update document status.
- Retrieve documents, extraction results, and processing jobs through an API.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
uvicorn document_processing_pipeline.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API docs.

## Test

```bash
pytest
```

## Key endpoints

- `POST /documents`
- `GET /documents`
- `GET /documents/{document_id}`
- `POST /documents/{document_id}/extract`
- `GET /documents/{document_id}/extraction`
- `POST /documents/{document_id}/process`
- `GET /jobs/{job_id}`
