"""PDF text extraction service with Gemini Vision OCR fallback."""

import logging
from dataclasses import dataclass, field
from typing import List, Optional

import fitz  # PyMuPDF

from app.config import MIN_TEXT_LENGTH
from app.services.ocr import ocr_page_image

logger = logging.getLogger(__name__)


@dataclass
class PageData:
    """Holds extracted text and metadata for a single PDF page."""
    page_number: int  # 1-indexed
    text: str = ""
    extraction_method: str = "direct"  # "direct" or "ocr"
    image_b64: Optional[str] = None  # base64-encoded page image for vision agents


@dataclass
class PDFParseResult:
    """Result of parsing an entire PDF."""
    pages: List[PageData] = field(default_factory=list)
    total_pages: int = 0
    ocr_pages: List[int] = field(default_factory=list)


def extract_text_from_pdf(pdf_bytes: bytes) -> PDFParseResult:
    """
    Extract text from each page of a PDF.
    Uses direct text extraction first, falls back to Gemini Vision OCR
    if text is too short.
    """
    import base64

    result = PDFParseResult()

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    result.total_pages = len(doc)
    logger.info("PDF opened: %d pages", result.total_pages)

    for page_idx in range(len(doc)):
        page_num = page_idx + 1
        page = doc[page_idx]

        # Try direct text extraction first
        text = page.get_text("text").strip()
        method = "direct"
        image_b64 = None

        if len(text) < MIN_TEXT_LENGTH:
            logger.info(
                "Page %d: direct text too short (%d chars), falling back to Gemini Vision OCR",
                page_num, len(text),
            )
            # Render page to image
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            image_b64 = base64.b64encode(img_bytes).decode("utf-8")

            # OCR via Gemini Vision
            ocr_text = ocr_page_image(img_bytes)
            if ocr_text and len(ocr_text.strip()) > len(text):
                text = ocr_text.strip()
                method = "ocr"
                result.ocr_pages.append(page_num)
            else:
                logger.warning("Page %d: OCR also returned minimal text", page_num)
                if not text:
                    text = ocr_text.strip() if ocr_text else ""
                    method = "ocr"
                    result.ocr_pages.append(page_num)

        result.pages.append(PageData(
            page_number=page_num,
            text=text,
            extraction_method=method,
            image_b64=image_b64,
        ))
        logger.info("Page %d [%s]: %d chars extracted", page_num, method, len(text))

    doc.close()
    return result
