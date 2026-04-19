"""Integration test for POST /api/process endpoint."""

import os
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

from app.main import app

SAMPLE_PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "final_image_protected.pdf")


@pytest.fixture
def mock_pipeline_result():
    """A mock result matching the expected response schema."""
    return {
        "claim_id": "TEST001",
        "status": "success",
        "documents": {
            "page_classification": [
                {"page_number": 1, "document_type": "identity_document", "confidence": 0.9},
                {"page_number": 2, "document_type": "discharge_summary", "confidence": 0.85},
                {"page_number": 3, "document_type": "itemized_bill", "confidence": 0.88},
            ],
            "routing": {
                "id_agent_pages": [1],
                "discharge_summary_pages": [2],
                "itemized_bill_pages": [3],
            },
        },
        "extracted_data": {
            "identity": {
                "patient_name": "Test Patient",
                "date_of_birth": "1990-01-01",
                "id_numbers": ["ID12345"],
                "policy_details": {
                    "policy_number": "POL001",
                    "insurer": "TestInsurer",
                    "plan_name": "Basic",
                },
            },
            "discharge_summary": {
                "diagnosis": ["Test Diagnosis"],
                "admission_date": "2024-01-01",
                "discharge_date": "2024-01-03",
                "physicians": ["Dr. Test"],
            },
            "itemized_bill": {
                "items": [
                    {"description": "Consultation", "quantity": 1, "unit_price": 200, "amount": 200},
                ],
                "reported_total": 200.0,
                "calculated_total": 200.0,
                "currency": "USD",
            },
        },
        "validation": {
            "total_consistency_check": True,
            "notes": [],
        },
        "metadata": {
            "page_count": 3,
            "ocr_pages": [1],
            "processing_time_ms": 500.0,
        },
    }


@pytest.mark.asyncio
async def test_process_endpoint_with_mock(mock_pipeline_result):
    """Test the /api/process endpoint with a mocked pipeline."""
    # Create a minimal valid PDF
    minimal_pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\nxref\n0 4\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n0\n%%EOF"

    with patch("app.api.routes.process_claim", new_callable=AsyncMock) as mock_process:
        mock_process.return_value = mock_pipeline_result

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/process",
                data={"claim_id": "TEST001"},
                files={"file": ("test.pdf", minimal_pdf, "application/pdf")},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["claim_id"] == "TEST001"
    assert data["status"] == "success"
    assert len(data["documents"]["page_classification"]) == 3
    assert data["extracted_data"]["identity"]["patient_name"] == "Test Patient"
    assert data["extracted_data"]["itemized_bill"]["calculated_total"] == 200.0
    assert data["validation"]["total_consistency_check"] is True


@pytest.mark.asyncio
async def test_process_endpoint_invalid_file():
    """Test that non-PDF files are rejected with 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/process",
            data={"claim_id": "TEST002"},
            files={"file": ("test.txt", b"not a pdf", "text/plain")},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_process_endpoint_empty_file():
    """Test that empty files are rejected with 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/process",
            data={"claim_id": "TEST003"},
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_process_endpoint_missing_claim_id():
    """Test that missing claim_id returns 422."""
    minimal_pdf = b"%PDF-1.4\ntest"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/process",
            files={"file": ("test.pdf", minimal_pdf, "application/pdf")},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_process_endpoint_not_a_pdf_content():
    """Test that a file with .pdf extension but non-PDF content is rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/process",
            data={"claim_id": "TEST004"},
            files={"file": ("fake.pdf", b"This is not a PDF file", "application/pdf")},
        )
    assert response.status_code == 400
