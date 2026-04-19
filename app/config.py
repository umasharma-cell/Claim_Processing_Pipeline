import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "tesseract")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Minimum text length threshold to consider direct extraction successful
MIN_TEXT_LENGTH = 50

# LLM retry settings
LLM_MAX_RETRIES = 3
LLM_TIMEOUT = 120
