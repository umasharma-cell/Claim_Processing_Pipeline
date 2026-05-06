# Document Processing Pipeline

AI-powered PDF document analysis and summary generation using **FastAPI**, **LangGraph**, and **Google Gemini**.

Upload any PDF and get an AI-generated summary, key topics, and document classification.

## Live Demo

| Service  | URL |
|----------|-----|
| Backend (API)  | [https://claim-processing-pipeline-l56y.onrender.com](https://claim-processing-pipeline-l56y.onrender.com) |
| Frontend (UI)  | *Deploying on Vercel — link will be updated* |
| API Docs       | [https://claim-processing-pipeline-l56y.onrender.com/docs](https://claim-processing-pipeline-l56y.onrender.com/docs) |
| Health Check   | [https://claim-processing-pipeline-l56y.onrender.com/health](https://claim-processing-pipeline-l56y.onrender.com/health) |

## Architecture

```
                     ┌─────────────────────┐
                     │   Next.js Frontend  │
                     │   (Vercel)          │
                     └──────────┬──────────┘
                                │ POST /api/process
                     ┌──────────▼──────────┐
                     │   FastAPI Backend   │
                     │   (Render)          │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │   PDF Parser +      │
                     │   OCR Fallback      │
                     │   (PyMuPDF/Gemini)  │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │   Summary Agent     │
                     │   (Gemini LLM)      │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │   JSON Response     │
                     │   (title, summary,  │
                     │    topics, type)    │
                     └─────────────────────┘
```

### LangGraph Pipeline

```
START → pdf_parse_node → summary_node → END
```

- **pdf_parse_node**: Extracts text from each PDF page using PyMuPDF. Falls back to Gemini Vision OCR for scanned/image pages (< 50 chars of text).
- **summary_node**: Sends combined page text to Google Gemini, returns a structured summary with title, description, key topics, and document type.

## Tech Stack

| Layer     | Technology |
|-----------|------------|
| Frontend  | Next.js 16, React 19, Tailwind CSS v4, TypeScript |
| Backend   | FastAPI, Python 3.11 |
| AI/LLM    | Google Gemini (via LangChain), LangGraph |
| PDF       | PyMuPDF (text extraction), Gemini Vision (OCR fallback) |
| Deploy    | Vercel (frontend), Render (backend) |

## Setup (Local Development)

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API key

### Backend

```bash
# Clone and enter the project
cd Claim_Processing_Pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run the backend
python -m uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

Frontend will be available at `http://localhost:3000`.

### Environment Variables

#### Backend (.env)

| Variable       | Description                     | Default            |
|----------------|---------------------------------|--------------------|
| `GOOGLE_API_KEY` | Google Gemini API key          | *(required)*       |
| `GEMINI_MODEL`   | Gemini model name              | `gemini-2.0-flash` |
| `LOG_LEVEL`      | Logging level                  | `INFO`             |
| `FRONTEND_URL`   | Deployed frontend URL (CORS)   | *(optional)*       |

#### Frontend

| Variable              | Description              | Default                  |
|-----------------------|--------------------------|--------------------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL     | `http://localhost:8000`  |

## API

### POST /api/process

Process a PDF document and return an AI-generated summary.

**Request:** `multipart/form-data`

| Field        | Type   | Description              |
|--------------|--------|--------------------------|
| `document_id` | string | Unique document identifier |
| `file`        | file   | PDF file to process       |

**cURL Example:**

```bash
curl -X POST https://claim-processing-pipeline-l56y.onrender.com/api/process \
  -F "document_id=DOC-001" \
  -F "file=@document.pdf"
```

**Python Example:**

```python
import requests

response = requests.post(
    "https://claim-processing-pipeline-l56y.onrender.com/api/process",
    data={"document_id": "DOC-001"},
    files={"file": open("document.pdf", "rb")},
)
print(response.json())
```

**Response:**

```json
{
  "document_id": "DOC-001",
  "status": "success",
  "title": "Mobile App Development Proposal",
  "summary": "This document outlines a proposal for building a cross-platform mobile application. It covers the project scope, timeline, technology stack (React Native), and estimated budget of $45,000. The proposal is addressed to Acme Corp from DevStudio Inc.",
  "key_topics": [
    "Mobile App Development",
    "React Native",
    "Project Proposal",
    "Budget Estimation"
  ],
  "document_type": "Business Proposal",
  "metadata": {
    "page_count": 3,
    "ocr_pages": [],
    "processing_time_ms": 4300.50
  }
}
```

### GET /health

Health check endpoint.

```bash
curl https://claim-processing-pipeline-l56y.onrender.com/health
# {"status": "healthy"}
```

## Deployment

### Backend (Render)

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repository
3. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `PYTHON_VERSION` = `3.11.12`
   - `GOOGLE_API_KEY` = your Gemini API key
   - `GEMINI_MODEL` = `gemini-2.0-flash`
   - `LOG_LEVEL` = `INFO`
   - `FRONTEND_URL` = your Vercel frontend URL (after deploying frontend)

### Frontend (Vercel)

1. Create a new project on [Vercel](https://vercel.com)
2. Connect your GitHub repository
3. Set **Root Directory** to `frontend`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://claim-processing-pipeline-l56y.onrender.com`
5. Deploy

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
│   │   └── summary_agent.py     # Document summary agent (Gemini)
│   ├── graph/
│   │   ├── __init__.py
│   │   └── workflow.py          # LangGraph pipeline definition
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic request/response models
│   └── services/
│       ├── __init__.py
│       ├── pdf_parser.py        # PDF text extraction (PyMuPDF)
│       └── ocr.py               # OCR fallback (Gemini Vision)
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Main page
│   │   │   ├── layout.tsx       # Root layout
│   │   │   └── globals.css      # Global styles
│   │   ├── components/
│   │   │   ├── UploadForm.tsx   # PDF upload with drag-and-drop
│   │   │   ├── ProcessingStatus.tsx  # Loading spinner
│   │   │   ├── ResultsPanel.tsx # Results container
│   │   │   ├── SummaryCard.tsx  # Summary display card
│   │   │   └── ErrorDisplay.tsx # Error state
│   │   ├── hooks/
│   │   │   └── useClaimProcessor.ts  # State management hook
│   │   └── lib/
│   │       ├── api.ts           # API client
│   │       └── types.ts         # TypeScript interfaces
│   ├── package.json
│   └── tsconfig.json
├── tests/
│   ├── test_routing.py
│   ├── test_bill_calculation.py
│   ├── test_schemas.py
│   └── test_integration.py
├── requirements.txt
├── .python-version              # Python 3.11 for Render
├── .env.example
└── README.md
```

## How It Works

1. **User uploads a PDF** via the Next.js frontend
2. **FastAPI receives** the file and passes it to the LangGraph pipeline
3. **PDF Parser** extracts text from each page using PyMuPDF; falls back to Gemini Vision OCR for scanned pages
4. **Summary Agent** sends the combined text to Google Gemini, which returns a structured analysis: title, summary, key topics, and document type
5. **Response** is sent back to the frontend and displayed in a clean card layout
