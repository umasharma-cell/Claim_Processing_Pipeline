"""Segregator Agent: classifies each page into document types and builds routing map."""

import json
import logging
import re
from typing import Any, Dict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import GOOGLE_API_KEY, GEMINI_MODEL, LLM_MAX_RETRIES, LLM_TIMEOUT

logger = logging.getLogger(__name__)

VALID_DOC_TYPES = [
    "claim_forms",
    "cheque_or_bank_details",
    "identity_document",
    "itemized_bill",
    "discharge_summary",
    "prescription",
    "investigation_report",
    "cash_receipt",
    "other",
]

# Maps doc types to extraction agent routing keys
DOC_TYPE_TO_AGENT = {
    "identity_document": "id_agent_pages",
    "claim_forms": "id_agent_pages",
    "cheque_or_bank_details": "id_agent_pages",
    "discharge_summary": "discharge_summary_pages",
    "prescription": "discharge_summary_pages",
    "investigation_report": "discharge_summary_pages",
    "itemized_bill": "itemized_bill_pages",
    "cash_receipt": "itemized_bill_pages",
}

SEGREGATOR_SYSTEM_PROMPT = """You are a document classification agent for insurance claim processing.

Given the text content of a single PDF page, classify it into exactly ONE of these document types:
- claim_forms: Insurance claim application forms
- cheque_or_bank_details: Cheque images or bank account details
- identity_document: Government IDs, patient ID cards, insurance cards, membership cards
- itemized_bill: Hospital/medical bills with line items, charges, amounts
- discharge_summary: Hospital discharge summaries with diagnosis, admission/discharge dates
- prescription: Doctor prescriptions, medication orders
- investigation_report: Lab reports, diagnostic test results, imaging reports
- cash_receipt: Payment receipts, cash memos
- other: Any document that doesn't fit the above categories

Respond ONLY with valid JSON in this exact format:
{
  "document_type": "<one of the types above>",
  "confidence": <float between 0.0 and 1.0>,
  "rationale": "<brief reason for classification>"
}
"""


def _build_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
        max_retries=LLM_MAX_RETRIES,
        timeout=LLM_TIMEOUT,
    )


def _parse_classification(raw: str) -> Dict[str, Any]:
    """Parse LLM output into a classification dict, with fallback."""
    # Try to extract JSON from the response
    json_match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            doc_type = parsed.get("document_type", "other")
            if doc_type not in VALID_DOC_TYPES:
                doc_type = "other"
            return {
                "document_type": doc_type,
                "confidence": float(parsed.get("confidence", 0.0)),
                "rationale": parsed.get("rationale", ""),
            }
        except (json.JSONDecodeError, ValueError):
            pass
    return {"document_type": "other", "confidence": 0.0, "rationale": "Failed to parse LLM output"}


def classify_pages(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Classify each page and return classification list + routing map.

    Args:
        pages: list of dicts with keys: page_number, text, extraction_method

    Returns:
        Dict with 'classifications' and 'routing' keys.
    """
    llm = _build_llm()
    classifications = []
    routing = {
        "id_agent_pages": [],
        "discharge_summary_pages": [],
        "itemized_bill_pages": [],
    }

    for page in pages:
        page_num = page["page_number"]
        text = page["text"]

        if not text.strip():
            classification = {
                "document_type": "other",
                "confidence": 0.0,
                "rationale": "Empty page - no text extracted",
            }
        else:
            # Truncate very long text to stay within token limits
            truncated_text = text[:4000] if len(text) > 4000 else text
            try:
                response = llm.invoke([
                    SystemMessage(content=SEGREGATOR_SYSTEM_PROMPT),
                    HumanMessage(content=f"Page {page_num} content:\n\n{truncated_text}"),
                ])
                classification = _parse_classification(response.content)
            except Exception as e:
                logger.error("Segregator LLM call failed for page %d: %s", page_num, str(e))
                classification = {
                    "document_type": "other",
                    "confidence": 0.0,
                    "rationale": f"LLM error: {str(e)}",
                }

        classifications.append({
            "page_number": page_num,
            **classification,
        })

        # Route to appropriate agent
        agent_key = DOC_TYPE_TO_AGENT.get(classification["document_type"])
        if agent_key:
            routing[agent_key].append(page_num)

        logger.info(
            "Page %d classified as '%s' (confidence: %.2f)",
            page_num, classification["document_type"], classification["confidence"],
        )

    return {"classifications": classifications, "routing": routing}
