"""LangGraph workflow: PDF Parse -> Summary -> END."""

import logging
import time
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import StateGraph, START, END

from app.services.pdf_parser import extract_text_from_pdf, PDFParseResult
from app.agents.summary_agent import generate_summary

logger = logging.getLogger(__name__)


# ── State definition ─────────────────────────────────────────────────────────

class PipelineState(TypedDict, total=False):
    # Input
    document_id: str
    pdf_bytes: bytes
    start_time: float

    # After PDF parsing
    pages: List[Dict[str, Any]]
    total_pages: int
    ocr_pages: List[int]

    # Final output
    result: Dict[str, Any]


# ── Node functions ───────────────────────────────────────────────────────────

def pdf_parse_node(state: PipelineState) -> Dict[str, Any]:
    """Parse PDF bytes into per-page text."""
    logger.info("=== PDF PARSE STAGE ===")
    parse_result: PDFParseResult = extract_text_from_pdf(state["pdf_bytes"])

    pages = [
        {
            "page_number": p.page_number,
            "text": p.text,
            "extraction_method": p.extraction_method,
        }
        for p in parse_result.pages
    ]

    return {
        "pages": pages,
        "total_pages": parse_result.total_pages,
        "ocr_pages": parse_result.ocr_pages,
    }


def summary_node(state: PipelineState) -> Dict[str, Any]:
    """Generate a document summary from parsed pages."""
    logger.info("=== SUMMARY STAGE ===")

    pages = state.get("pages", [])
    summary_data = generate_summary(pages)

    elapsed_ms = round((time.time() - state["start_time"]) * 1000, 2)

    result = {
        "document_id": state["document_id"],
        "status": "success",
        "title": summary_data.get("title"),
        "summary": summary_data.get("summary"),
        "key_topics": summary_data.get("key_topics", []),
        "document_type": summary_data.get("document_type"),
        "metadata": {
            "page_count": state.get("total_pages", 0),
            "ocr_pages": state.get("ocr_pages", []),
            "processing_time_ms": elapsed_ms,
        },
    }

    logger.info("Summary complete. Processing time: %.2f ms", elapsed_ms)
    return {"result": result}


# ── Build the graph ──────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """Build and compile the LangGraph processing pipeline."""
    graph = StateGraph(PipelineState)

    graph.add_node("pdf_parse_node", pdf_parse_node)
    graph.add_node("summary_node", summary_node)

    graph.add_edge(START, "pdf_parse_node")
    graph.add_edge("pdf_parse_node", "summary_node")
    graph.add_edge("summary_node", END)

    return graph.compile()


async def process_document(document_id: str, pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Run the full document processing pipeline.

    Args:
        document_id: The document identifier.
        pdf_bytes: Raw PDF file bytes.

    Returns:
        Final result dict with summary.
    """
    compiled_graph = build_graph()

    initial_state: PipelineState = {
        "document_id": document_id,
        "pdf_bytes": pdf_bytes,
        "start_time": time.time(),
    }

    logger.info("Starting pipeline for document_id=%s", document_id)
    final_state = await compiled_graph.ainvoke(initial_state)
    logger.info("Pipeline completed for document_id=%s", document_id)

    return final_state["result"]
