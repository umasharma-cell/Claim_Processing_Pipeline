"""Discharge Summary Agent: extracts diagnosis and admission details from assigned pages."""

import json
import logging
import re
from typing import Any, Dict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import GOOGLE_API_KEY, GEMINI_MODEL, LLM_MAX_RETRIES, LLM_TIMEOUT

logger = logging.getLogger(__name__)

DISCHARGE_AGENT_SYSTEM_PROMPT = """You are a medical discharge summary extraction agent for insurance claims.

Given text from discharge summaries, prescriptions, or investigation reports, extract:
- diagnosis: List of all diagnoses mentioned
- admission_date: Date of hospital admission (any format found)
- discharge_date: Date of hospital discharge (any format found)
- physicians: List of doctor/physician names mentioned

If a field is not found, use null for strings and empty list [] for arrays.

Respond ONLY with valid JSON in this exact format:
{
  "diagnosis": ["diagnosis1", "diagnosis2"],
  "admission_date": "string or null",
  "discharge_date": "string or null",
  "physicians": ["Dr. Name1", "Dr. Name2"]
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


def _parse_discharge_output(raw: str) -> Dict[str, Any]:
    """Parse LLM output into discharge summary data dict."""
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            return {
                "diagnosis": parsed.get("diagnosis", []) or [],
                "admission_date": parsed.get("admission_date"),
                "discharge_date": parsed.get("discharge_date"),
                "physicians": parsed.get("physicians", []) or [],
            }
        except (json.JSONDecodeError, ValueError):
            pass
    return {
        "diagnosis": [],
        "admission_date": None,
        "discharge_date": None,
        "physicians": [],
    }


def extract_discharge_summary(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract discharge summary information from assigned pages.

    Args:
        pages: list of dicts with keys: page_number, text

    Returns:
        Discharge summary extraction result dict.
    """
    if not pages:
        logger.info("Discharge Agent: no pages assigned, returning defaults")
        return _parse_discharge_output("")

    llm = _build_llm()

    combined_text = "\n\n".join(
        f"--- Page {p['page_number']} ---\n{p['text']}" for p in pages
    )
    combined_text = combined_text[:8000]

    try:
        response = llm.invoke([
            SystemMessage(content=DISCHARGE_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=f"Extract discharge summary information from these pages:\n\n{combined_text}"),
        ])
        result = _parse_discharge_output(response.content)
        logger.info("Discharge Agent extracted: %d diagnoses", len(result["diagnosis"]))
        return result
    except Exception as e:
        logger.error("Discharge Agent LLM call failed: %s", str(e))
        return _parse_discharge_output("")
