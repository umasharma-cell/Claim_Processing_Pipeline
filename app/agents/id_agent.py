"""ID Agent: extracts identity and policy information from assigned pages."""

import json
import logging
import re
from typing import Any, Dict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import GOOGLE_API_KEY, GEMINI_MODEL, LLM_MAX_RETRIES, LLM_TIMEOUT

logger = logging.getLogger(__name__)

ID_AGENT_SYSTEM_PROMPT = """You are an identity information extraction agent for insurance claims.

Given text from document pages (identity documents, claim forms, bank details), extract the following:
- patient_name: Full name of the patient/claimant
- date_of_birth: Date of birth in any format found
- id_numbers: List of any ID numbers (government ID, member ID, patient ID, SSN, etc.)
- policy_details:
  - policy_number: Insurance policy number
  - insurer: Name of insurance company
  - plan_name: Name of the insurance plan

If a field is not found, use null for strings and empty list [] for arrays.

Respond ONLY with valid JSON in this exact format:
{
  "patient_name": "string or null",
  "date_of_birth": "string or null",
  "id_numbers": ["id1", "id2"],
  "policy_details": {
    "policy_number": "string or null",
    "insurer": "string or null",
    "plan_name": "string or null"
  }
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


def _parse_id_output(raw: str) -> Dict[str, Any]:
    """Parse LLM output into identity data dict."""
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            return {
                "patient_name": parsed.get("patient_name"),
                "date_of_birth": parsed.get("date_of_birth"),
                "id_numbers": parsed.get("id_numbers", []) or [],
                "policy_details": {
                    "policy_number": parsed.get("policy_details", {}).get("policy_number"),
                    "insurer": parsed.get("policy_details", {}).get("insurer"),
                    "plan_name": parsed.get("policy_details", {}).get("plan_name"),
                },
            }
        except (json.JSONDecodeError, ValueError, AttributeError):
            pass
    return {
        "patient_name": None,
        "date_of_birth": None,
        "id_numbers": [],
        "policy_details": {"policy_number": None, "insurer": None, "plan_name": None},
    }


def extract_identity(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract identity information from assigned pages.

    Args:
        pages: list of dicts with keys: page_number, text

    Returns:
        Identity extraction result dict.
    """
    if not pages:
        logger.info("ID Agent: no pages assigned, returning defaults")
        return _parse_id_output("")

    llm = _build_llm()

    # Combine text from all assigned pages
    combined_text = "\n\n".join(
        f"--- Page {p['page_number']} ---\n{p['text']}" for p in pages
    )
    # Truncate to fit token limits
    combined_text = combined_text[:8000]

    try:
        response = llm.invoke([
            SystemMessage(content=ID_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=f"Extract identity information from these pages:\n\n{combined_text}"),
        ])
        result = _parse_id_output(response.content)
        logger.info("ID Agent extracted: patient_name=%s", result.get("patient_name"))
        return result
    except Exception as e:
        logger.error("ID Agent LLM call failed: %s", str(e))
        return _parse_id_output("")
