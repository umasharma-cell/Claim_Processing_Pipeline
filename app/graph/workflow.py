"""LangGraph workflow: Segregator -> [ID, Discharge, Bill] -> Aggregator."""

import logging
import time
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import StateGraph, START, END

from app.services.pdf_parser import extract_text_from_pdf, PDFParseResult
from app.agents.segregator import classify_pages
from app.agents.id_agent import extract_identity
from app.agents.discharge_agent import extract_discharge_summary
from app.agents.bill_agent import extract_itemized_bill, calculate_total

logger = logging.getLogger(__name__)


# ── State definition ─────────────────────────────────────────────────────────

class PipelineState(TypedDict, total=False):
    # Input
    claim_id: str
    pdf_bytes: bytes
    start_time: float

    # After PDF parsing
    pages: List[Dict[str, Any]]
    total_pages: int
    ocr_pages: List[int]

    # After segregation
    classifications: List[Dict[str, Any]]
    routing: Dict[str, List[int]]

    # After extraction
    identity_data: Dict[str, Any]
    discharge_data: Dict[str, Any]
    bill_data: Dict[str, Any]

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


def segregator_node(state: PipelineState) -> Dict[str, Any]:
    """Classify pages and create routing map."""
    logger.info("=== SEGREGATION STAGE ===")
    result = classify_pages(state["pages"])
    logger.info("Routing: %s", {k: v for k, v in result["routing"].items() if v})
    return {
        "classifications": result["classifications"],
        "routing": result["routing"],
    }


def _get_pages_for_agent(state: PipelineState, agent_key: str) -> List[Dict[str, Any]]:
    """Get only the pages assigned to a specific agent."""
    assigned_page_nums = set(state["routing"].get(agent_key, []))
    return [
        {"page_number": p["page_number"], "text": p["text"]}
        for p in state["pages"]
        if p["page_number"] in assigned_page_nums
    ]


def id_agent_node(state: PipelineState) -> Dict[str, Any]:
    """Extract identity information from assigned pages only."""
    logger.info("=== ID AGENT STAGE ===")
    pages = _get_pages_for_agent(state, "id_agent_pages")
    logger.info("ID Agent processing %d pages: %s", len(pages), [p["page_number"] for p in pages])
    return {"identity_data": extract_identity(pages)}


def discharge_summary_node(state: PipelineState) -> Dict[str, Any]:
    """Extract discharge summary from assigned pages only."""
    logger.info("=== DISCHARGE SUMMARY AGENT STAGE ===")
    pages = _get_pages_for_agent(state, "discharge_summary_pages")
    logger.info("Discharge Agent processing %d pages: %s", len(pages), [p["page_number"] for p in pages])
    return {"discharge_data": extract_discharge_summary(pages)}


def itemized_bill_node(state: PipelineState) -> Dict[str, Any]:
    """Extract itemized bill from assigned pages only."""
    logger.info("=== ITEMIZED BILL AGENT STAGE ===")
    pages = _get_pages_for_agent(state, "itemized_bill_pages")
    logger.info("Bill Agent processing %d pages: %s", len(pages), [p["page_number"] for p in pages])
    return {"bill_data": extract_itemized_bill(pages)}


def aggregator_node(state: PipelineState) -> Dict[str, Any]:
    """Merge all agent outputs into the final response JSON."""
    logger.info("=== AGGREGATION STAGE ===")

    identity = state.get("identity_data", {})
    discharge = state.get("discharge_data", {})
    bill = state.get("bill_data", {})

    # Validation: check total consistency
    reported = bill.get("reported_total")
    calculated = bill.get("calculated_total")
    notes = []
    total_check = None

    if reported is not None and calculated is not None:
        total_check = abs(reported - calculated) < 0.01
        if not total_check:
            notes.append(
                f"Total mismatch: reported={reported}, calculated={calculated}"
            )
    elif reported is None and calculated is None and not bill.get("items"):
        notes.append("No bill items extracted")
    else:
        notes.append("Could not perform total consistency check (missing data)")

    elapsed_ms = round((time.time() - state["start_time"]) * 1000, 2)

    result = {
        "claim_id": state["claim_id"],
        "status": "success",
        "documents": {
            "page_classification": [
                {
                    "page_number": c["page_number"],
                    "document_type": c["document_type"],
                    "confidence": c.get("confidence", 0.0),
                }
                for c in state.get("classifications", [])
            ],
            "routing": state.get("routing", {
                "id_agent_pages": [],
                "discharge_summary_pages": [],
                "itemized_bill_pages": [],
            }),
        },
        "extracted_data": {
            "identity": {
                "patient_name": identity.get("patient_name"),
                "date_of_birth": identity.get("date_of_birth"),
                "id_numbers": identity.get("id_numbers", []),
                "policy_details": identity.get("policy_details", {
                    "policy_number": None,
                    "insurer": None,
                    "plan_name": None,
                }),
            },
            "discharge_summary": {
                "diagnosis": discharge.get("diagnosis", []),
                "admission_date": discharge.get("admission_date"),
                "discharge_date": discharge.get("discharge_date"),
                "physicians": discharge.get("physicians", []),
            },
            "itemized_bill": {
                "items": [
                    {
                        "description": item.get("description"),
                        "quantity": item.get("quantity"),
                        "unit_price": item.get("unit_price"),
                        "amount": item.get("amount"),
                    }
                    for item in bill.get("items", [])
                ],
                "reported_total": reported,
                "calculated_total": calculated,
                "currency": bill.get("currency"),
            },
        },
        "validation": {
            "total_consistency_check": total_check,
            "notes": notes,
        },
        "metadata": {
            "page_count": state.get("total_pages", 0),
            "ocr_pages": state.get("ocr_pages", []),
            "processing_time_ms": elapsed_ms,
        },
    }

    logger.info("Aggregation complete. Processing time: %.2f ms", elapsed_ms)
    return {"result": result}


# ── Build the graph ──────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """Build and compile the LangGraph processing pipeline."""
    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("pdf_parse_node", pdf_parse_node)
    graph.add_node("segregator_node", segregator_node)
    graph.add_node("id_agent_node", id_agent_node)
    graph.add_node("discharge_summary_node", discharge_summary_node)
    graph.add_node("itemized_bill_node", itemized_bill_node)
    graph.add_node("aggregator_node", aggregator_node)

    # Define edges: START -> pdf_parse -> segregator -> [3 agents] -> aggregator -> END
    graph.add_edge(START, "pdf_parse_node")
    graph.add_edge("pdf_parse_node", "segregator_node")

    # Fan-out from segregator to all 3 extraction agents
    graph.add_edge("segregator_node", "id_agent_node")
    graph.add_edge("segregator_node", "discharge_summary_node")
    graph.add_edge("segregator_node", "itemized_bill_node")

    # Fan-in: all 3 agents -> aggregator
    graph.add_edge("id_agent_node", "aggregator_node")
    graph.add_edge("discharge_summary_node", "aggregator_node")
    graph.add_edge("itemized_bill_node", "aggregator_node")

    graph.add_edge("aggregator_node", END)

    return graph.compile()


async def process_claim(claim_id: str, pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Run the full claim processing pipeline.

    Args:
        claim_id: The claim identifier.
        pdf_bytes: Raw PDF file bytes.

    Returns:
        Final aggregated result dict.
    """
    compiled_graph = build_graph()

    initial_state: PipelineState = {
        "claim_id": claim_id,
        "pdf_bytes": pdf_bytes,
        "start_time": time.time(),
    }

    logger.info("Starting pipeline for claim_id=%s", claim_id)
    final_state = await compiled_graph.ainvoke(initial_state)
    logger.info("Pipeline completed for claim_id=%s", claim_id)

    return final_state["result"]
