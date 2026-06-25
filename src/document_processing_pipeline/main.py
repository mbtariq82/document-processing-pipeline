from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from document_processing_pipeline.domain import DocumentError, NotFoundError, ValidationError
from document_processing_pipeline.extraction import ExtractionService
from document_processing_pipeline.ingestion import IngestionService
from document_processing_pipeline.processing import ProcessingService
from document_processing_pipeline.repository import DocumentRepository
from document_processing_pipeline.schemas import (
    DocumentResponse,
    ExtractionResponse,
    HealthResponse,
    IngestDocumentRequest,
    ProcessingJobResponse,
)


def create_app(repository: DocumentRepository | None = None) -> FastAPI:
    repository = repository or DocumentRepository()
    ingestion_service = IngestionService(repository)
    extraction_service = ExtractionService(repository)
    processing_service = ProcessingService(repository, extraction_service)

    app = FastAPI(
        title="Document Processing Pipeline",
        version="0.1.0",
        summary="Document ingestion, extraction, and processing API.",
    )
    app.state.repository = repository
    app.state.ingestion_service = ingestion_service
    app.state.extraction_service = extraction_service
    app.state.processing_service = processing_service

    @app.exception_handler(DocumentError)
    async def handle_document_error(_request: Request, exc: DocumentError) -> JSONResponse:
        status_code = status.HTTP_400_BAD_REQUEST
        if isinstance(exc, NotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, ValidationError):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/documents", status_code=status.HTTP_201_CREATED, response_model=DocumentResponse)
    def ingest_document(payload: IngestDocumentRequest) -> DocumentResponse:
        return DocumentResponse.model_validate(
            ingestion_service.ingest(
                payload.filename,
                payload.content,
                payload.mime_type,
                payload.metadata,
            )
        )

    @app.get("/documents", response_model=list[DocumentResponse])
    def list_documents() -> list[DocumentResponse]:
        return [DocumentResponse.model_validate(document) for document in repository.list_documents()]

    @app.get("/documents/{document_id}", response_model=DocumentResponse)
    def get_document(document_id: str) -> DocumentResponse:
        return DocumentResponse.model_validate(repository.get_document(document_id))

    @app.post("/documents/{document_id}/extract", response_model=ExtractionResponse)
    def extract_document(document_id: str) -> ExtractionResponse:
        return ExtractionResponse.model_validate(extraction_service.extract(document_id))

    @app.get("/documents/{document_id}/extraction", response_model=ExtractionResponse)
    def get_extraction(document_id: str) -> ExtractionResponse:
        return ExtractionResponse.model_validate(repository.get_extraction(document_id))

    @app.post("/documents/{document_id}/process", response_model=ProcessingJobResponse)
    def process_document(document_id: str) -> ProcessingJobResponse:
        return ProcessingJobResponse.model_validate(processing_service.process(document_id))

    @app.get("/jobs/{job_id}", response_model=ProcessingJobResponse)
    def get_job(job_id: str) -> ProcessingJobResponse:
        return ProcessingJobResponse.model_validate(repository.get_job(job_id))

    return app


app = create_app()
