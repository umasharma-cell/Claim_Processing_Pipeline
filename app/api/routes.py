"""FastAPI routes for document processing."""

import logging
from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.graph.workflow import process_document
from app.models.schemas import ProcessResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/process", response_model=ProcessResponse)
async def process_pdf(
    document_id: str = Form(..., description="Unique document identifier"),
    file: UploadFile = File(..., description="PDF file to process"),
):
    """
    Process a PDF document through the summary pipeline.

    - Accepts a document_id and PDF file via multipart form-data.
    - Returns structured JSON with document summary and key topics.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are accepted.",
        )

    if file.content_type and file.content_type not in (
        "application/pdf",
        "application/octet-stream",
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type: {file.content_type}. Expected application/pdf.",
        )

    # Read file bytes
    try:
        pdf_bytes = await file.read()
    except Exception as e:
        logger.error("Failed to read uploaded file: %s", str(e))
        raise HTTPException(status_code=422, detail="Failed to read uploaded file.")

    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Validate it's actually a PDF (check magic bytes)
    if not pdf_bytes[:5] == b"%PDF-":
        raise HTTPException(
            status_code=400,
            detail="File does not appear to be a valid PDF.",
        )

    # Process through pipeline
    try:
        logger.info("Processing document_id=%s, file=%s", document_id, file.filename)
        result = await process_document(document_id, pdf_bytes)
        return ProcessResponse(**result)
    except Exception as e:
        logger.exception("Processing failed for document_id=%s", document_id)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the document. Please try again.",
        )
