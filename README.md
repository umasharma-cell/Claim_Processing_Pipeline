# Claim Processing Pipeline

AI-powered document processing pipeline for insurance claim extraction using **FastAPI** and **LangGraph**.

## Architecture

```
                         ┌─────────────────┐
                         │   POST /api/    │
                         │    process      │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │  PDF Parser +   │
                         │  OCR Fallback   │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │  Segregator     │
                         │  Agent (AI)     │
                         └──┬─────┬─────┬──┘
                            │     │     │
              ┌─────────────┘     │     └─────────────┐
              │                   │                   │
     ┌────────▼────────┐ ┌───────▼────────┐ ┌────────▼────────┐
     │   ID Agent      │ │  Discharge     │ │  Itemized Bill  │
     │  (identity,     │ │  Summary Agent │ │  Agent          │
     │   policy)       │ │  (diagnosis,   │ │  (line items,   │
     │                 │ │   dates)       │ │   totals)       │
     └────────┬────────┘ └───────┬────────┘ └────────┬────────┘
              │                   │                   │
              └─────────────┬─────┘─────────────┬─────┘
                            │                   │
                         ┌──▼───────────────────▼──┐
                         │      Aggregator         │
                         │   (merge + validate)    │
                         └────────────┬────────────┘
                                      │
                                ┌─────▼─────┐
                                │  JSON     │
                                │  Response │
                                └───────────┘
```

### LangGraph Flow

```
START → pdf_parse_node → segregator_node → ┬→ id_agent_node          ─┬→ aggregator_node → END
                                           ├→ discharge_summary_node ─┤
                                           └→ itemized_bill_node     ─┘
```

## How Segregator Classification Works

The Segregator Agent uses an LLM (GPT-4o by default) to classify each PDF page into one of 9 document types:

1. **Per-page text extraction**: Each page's text is extracted via direct PDF parsing (PyMuPDF). If direct extraction yields too little text (< 50 chars), OCR is used as a fallback via pytesseract.

2. **AI classification**: The extracted text is sent to the LLM with a structured prompt that defines the 9 document categories. The LLM returns a JSON with `document_type`, `confidence` score, and `rationale`.

3. **Deterministic routing**: The classification is post-processed with a static routing map (`DOC_TYPE_TO_AGENT`) that assigns each document type to the correct extraction agent. This makes routing deterministic and auditable.

4. **Selective dispatch**: Only the pages assigned to each agent are sent to that agent — the full PDF is never passed to individual extractors.

## Setup

### Prerequisites

- Python 3.10+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and on PATH
- Google Gemini API key

### Installation

```bash
# Clone and enter the project
cd Claim_Processing_Pipeline

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and set your values:

| Variable        | Description                        | Default          |
|-----------------|------------------------------------|------------------|
| `GOOGLE_API_KEY`| Your Google Gemini API key         | *(required)*     |
| `GEMINI_MODEL`  | Gemini model to use                | `gemini-2.0-flash`|
| `TESSERACT_CMD` | Path to tesseract binary           | `tesseract`  |
| `LOG_LEVEL`     | Logging level (DEBUG/INFO/WARNING) | `INFO`       |

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

- Swagger UI: `http://localhost:8000/docs`
- Health check: `GET http://localhost:8000/health`

## Test

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_routing.py -v
python -m pytest tests/test_bill_calculation.py -v
python -m pytest tests/test_schemas.py -v
python -m pytest tests/test_integration.py -v
```

## Sample API Request

### cURL

```bash
curl -X POST http://localhost:8000/api/process \
  -F "claim_id=CLM-2024-001" \
  -F "file=@final_image_protected.pdf"
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/process",
    data={"claim_id": "CLM-2024-001"},
    files={"file": open("final_image_protected.pdf", "rb")},
)
print(response.json())
```

### Sample Response

```json
{
  "claim_id": "CLM-2024-001",
  "status": "success",
  "documents": {
    "page_classification": [
      {"page_number": 1, "document_type": "identity_document", "confidence": 0.92},
      {"page_number": 2, "document_type": "discharge_summary", "confidence": 0.88},
      {"page_number": 3, "document_type": "itemized_bill", "confidence": 0.95}
    ],
    "routing": {
      "id_agent_pages": [1],
      "discharge_summary_pages": [2],
      "itemized_bill_pages": [3]
    }
  },
  "extracted_data": {
    "identity": {
      "patient_name": "John Doe",
      "date_of_birth": "1985-03-15",
      "id_numbers": ["GOV123456"],
      "policy_details": {
        "policy_number": "POL-789",
        "insurer": "HealthCare Inc.",
        "plan_name": "Premium Gold"
      }
    },
    "discharge_summary": {
      "diagnosis": ["Acute Appendicitis"],
      "admission_date": "2024-01-10",
      "discharge_date": "2024-01-13",
      "physicians": ["Dr. Jane Smith"]
    },
    "itemized_bill": {
      "items": [
        {"description": "Room Charges", "quantity": 3, "unit_price": 500.0, "amount": 1500.0},
        {"description": "Surgery", "quantity": 1, "unit_price": 5000.0, "amount": 5000.0}
      ],
      "reported_total": 6500.0,
      "calculated_total": 6500.0,
      "currency": "USD"
    }
  },
  "validation": {
    "total_consistency_check": true,
    "notes": []
  },
  "metadata": {
    "page_count": 3,
    "ocr_pages": [1, 2],
    "processing_time_ms": 12345.67
  }
}
```

## Project Structure

```
Claim_Processing_Pipeline/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Configuration & env vars
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py            # POST /api/process endpoint
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── segregator.py        # Page classification agent
│   │   ├── id_agent.py          # Identity extraction agent
│   │   ├── discharge_agent.py   # Discharge summary agent
│   │   └── bill_agent.py        # Itemized bill agent
│   ├── graph/
│   │   ├── __init__.py
│   │   └── workflow.py          # LangGraph pipeline definition
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic request/response models
│   └── services/
│       ├── __init__.py
│       ├── pdf_parser.py        # PDF text extraction
│       └── ocr.py               # OCR fallback service
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_routing.py          # Page routing logic tests
│   ├── test_bill_calculation.py # Total calculation tests
│   ├── test_schemas.py          # Response schema tests
│   └── test_integration.py      # API endpoint integration tests
├── final_image_protected.pdf    # Sample test PDF
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```
