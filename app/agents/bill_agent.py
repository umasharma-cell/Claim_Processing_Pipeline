"""Itemized Bill Agent: extracts line items and totals from assigned pages."""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import GOOGLE_API_KEY, GEMINI_MODEL, LLM_MAX_RETRIES, LLM_TIMEOUT

logger = logging.getLogger(__name__)

BILL_AGENT_SYSTEM_PROMPT = """You are a medical bill extraction agent for insurance claims.

Given text from itemized bills or cash receipts, extract:
- items: List of line items, each with description, quantity, unit_price, and amount
- reported_total: The total amount as printed/stated on the bill
- currency: The currency (e.g., "USD", "INR", "EUR")

For numeric fields, return numbers only (no currency symbols or commas).
If a field is not found, use null.

Respond ONLY with valid JSON in this exact format:
{
  "items": [
    {
      "description": "string",
      "quantity": 1.0,
      "unit_price": 100.0,
      "amount": 100.0
    }
  ],
  "reported_total": 500.0,
  "currency": "USD"
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


def _safe_float(val: Any) -> Optional[float]:
    """Safely convert a value to float."""
    if val is None:
        return None
    try:
        if isinstance(val, str):
            val = val.replace(",", "").strip()
        return float(val)
    except (ValueError, TypeError):
        return None


def calculate_total(items: List[Dict[str, Any]]) -> Optional[float]:
    """Calculate total from line items by summing amounts."""
    amounts = [_safe_float(item.get("amount")) for item in items]
    valid_amounts = [a for a in amounts if a is not None]
    if not valid_amounts:
        return None
    return round(sum(valid_amounts), 2)


def _parse_bill_output(raw: str) -> Dict[str, Any]:
    """Parse LLM output into bill data dict."""
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            items = []
            for item in parsed.get("items", []):
                items.append({
                    "description": item.get("description"),
                    "quantity": _safe_float(item.get("quantity")),
                    "unit_price": _safe_float(item.get("unit_price")),
                    "amount": _safe_float(item.get("amount")),
                })

            reported_total = _safe_float(parsed.get("reported_total"))
            calculated_total = calculate_total(items)

            return {
                "items": items,
                "reported_total": reported_total,
                "calculated_total": calculated_total,
                "currency": parsed.get("currency"),
            }
        except (json.JSONDecodeError, ValueError):
            pass
    return {
        "items": [],
        "reported_total": None,
        "calculated_total": None,
        "currency": None,
    }


def extract_itemized_bill(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract itemized bill information from assigned pages.

    Args:
        pages: list of dicts with keys: page_number, text

    Returns:
        Itemized bill extraction result dict.
    """
    if not pages:
        logger.info("Bill Agent: no pages assigned, returning defaults")
        return _parse_bill_output("")

    llm = _build_llm()

    combined_text = "\n\n".join(
        f"--- Page {p['page_number']} ---\n{p['text']}" for p in pages
    )
    combined_text = combined_text[:8000]

    try:
        response = llm.invoke([
            SystemMessage(content=BILL_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=f"Extract itemized bill information from these pages:\n\n{combined_text}"),
        ])
        result = _parse_bill_output(response.content)
        logger.info(
            "Bill Agent extracted: %d items, reported_total=%s, calculated_total=%s",
            len(result["items"]), result["reported_total"], result["calculated_total"],
        )
        return result
    except Exception as e:
        logger.error("Bill Agent LLM call failed: %s", str(e))
        return _parse_bill_output("")
