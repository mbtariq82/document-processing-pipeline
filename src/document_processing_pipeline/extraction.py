from __future__ import annotations

import re

from document_processing_pipeline.domain import ExtractionResult
from document_processing_pipeline.repository import DocumentRepository


class ExtractionService:
    FIELD_PATTERN = re.compile(r"^(?P<key>[A-Za-z][A-Za-z ]{1,40}):\s*(?P<value>.+)$")
    EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

    def __init__(self, repository: DocumentRepository) -> None:
        self.repository = repository

    def extract(self, document_id: str) -> ExtractionResult:
        document = self.repository.get_document(document_id)
        fields: dict[str, str] = {}
        for line in document.content.splitlines():
            match = self.FIELD_PATTERN.match(line.strip())
            if match:
                key = match.group("key").strip().lower().replace(" ", "_")
                fields[key] = match.group("value").strip()

        result = ExtractionResult(
            document_id=document.id,
            text=document.content,
            fields=fields,
            entities={"emails": self.EMAIL_PATTERN.findall(document.content)},
        )
        return self.repository.save_extraction(result)
