"""Pydantic models for request/response schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


# ── Request ──────────────────────────────────────────────────────────────────

class ProcessRequest(BaseModel):
    document_id: str


# ── Metadata ─────────────────────────────────────────────────────────────────

class ProcessingMetadata(BaseModel):
    page_count: int = 0
    ocr_pages: List[int] = Field(default_factory=list)
    processing_time_ms: float = 0


# ── Final response ───────────────────────────────────────────────────────────

class ProcessResponse(BaseModel):
    document_id: str
    status: str = "success"
    title: Optional[str] = None
    summary: Optional[str] = None
    key_topics: List[str] = Field(default_factory=list)
    document_type: Optional[str] = None
    metadata: ProcessingMetadata = Field(default_factory=ProcessingMetadata)
