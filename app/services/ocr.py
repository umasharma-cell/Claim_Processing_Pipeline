"""OCR service using Gemini Vision for extracting text from page images."""

import base64
import logging
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from app.config import GOOGLE_API_KEY, GEMINI_MODEL, LLM_MAX_RETRIES, LLM_TIMEOUT

logger = logging.getLogger(__name__)


def ocr_page_image(image_bytes: bytes) -> Optional[str]:
    """
    Run OCR on a PNG image using Gemini Vision and return extracted text.

    Args:
        image_bytes: PNG image bytes of a rendered PDF page.

    Returns:
        Extracted text string, or empty string on failure.
    """
    try:
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0,
            max_retries=LLM_MAX_RETRIES,
            timeout=LLM_TIMEOUT,
        )

        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Extract ALL text from this document image. Return only the raw text content, preserving the layout as much as possible. Do not add any commentary or explanation.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64_image}"},
                },
            ]
        )

        response = llm.invoke([message])
        text = response.content.strip() if response.content else ""
        logger.debug("Gemini Vision OCR extracted %d characters", len(text))
        return text
    except Exception as e:
        logger.error("Gemini Vision OCR failed: %s", str(e))
        return ""
