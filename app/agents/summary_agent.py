"""Summary Agent: generates a human-readable summary from PDF page text using Gemini."""

import json
import logging
import re
from typing import Any, Dict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import GOOGLE_API_KEY, GEMINI_MODEL, LLM_MAX_RETRIES, LLM_TIMEOUT

logger = logging.getLogger(__name__)

SUMMARY_SYSTEM_PROMPT = """You are a document analysis agent. Given the text content of a PDF document, produce a structured analysis.

Respond ONLY with valid JSON in this exact format:
{
  "title": "A brief, descriptive title for the document",
  "summary": "A clear 3-5 sentence summary explaining what this document is about, its purpose, and key information it contains.",
  "key_topics": ["topic1", "topic2", "topic3"],
  "document_type": "The type of document, e.g. research paper, invoice, legal contract, medical report, resume, letter, manual, etc."
}

Guidelines:
- The title should be concise (under 10 words) and capture the essence of the document.
- The summary should be informative and readable by someone who has not seen the document.
- List 3-6 key topics or themes found in the document.
- Be specific about the document type.
- If the text is too short or unclear to analyze, still provide your best assessment.
"""


def _build_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3,
        max_retries=LLM_MAX_RETRIES,
        timeout=LLM_TIMEOUT,
    )


def _parse_summary_output(raw: str) -> Dict[str, Any]:
    """Parse LLM output into summary data dict."""
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            return {
                "title": parsed.get("title") or None,
                "summary": parsed.get("summary") or None,
                "key_topics": parsed.get("key_topics", []) or [],
                "document_type": parsed.get("document_type") or None,
            }
        except (json.JSONDecodeError, ValueError):
            pass
    return {
        "title": None,
        "summary": None,
        "key_topics": [],
        "document_type": None,
    }


def generate_summary(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a summary from page text content.

    Args:
        pages: list of dicts with keys: page_number, text

    Returns:
        Summary result dict with title, summary, key_topics, document_type.
    """
    if not pages:
        logger.info("Summary Agent: no pages provided, returning defaults")
        return _parse_summary_output("")

    llm = _build_llm()

    combined_text = "\n\n".join(
        f"--- Page {p['page_number']} ---\n{p['text']}" for p in pages
    )
    # Truncate to stay within token limits
    combined_text = combined_text[:12000]

    try:
        response = llm.invoke([
            SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
            HumanMessage(content=f"Analyze this document and provide a structured summary:\n\n{combined_text}"),
        ])
        result = _parse_summary_output(response.content)
        logger.info("Summary Agent: title=%s, type=%s", result["title"], result["document_type"])
        return result
    except Exception as e:
        logger.error("Summary Agent LLM call failed: %s", str(e))
        return _parse_summary_output("")
