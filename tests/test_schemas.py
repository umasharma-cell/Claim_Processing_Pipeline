"""Unit tests for response schema validation."""

import pytest
from app.models.schemas import (
    ProcessResponse,
    PageClassification,
    RoutingMap,
    DocumentInfo,
    IdentityData,
    DischargeSummaryData,
    ItemizedBillData,
    BillItem,
    PolicyDetails,
    ExtractedData,
    Validation,
    ProcessingMetadata,
)


class TestProcessResponseSchema:
    def test_minimal_valid_response(self):
        response = ProcessResponse(claim_id="CLM001")
        assert response.claim_id == "CLM001"
        assert response.status == "success"
        assert response.documents.page_classification == []
        assert response.documents.routing.id_agent_pages == []
        assert response.extracted_data.identity.patient_name is None
        assert response.metadata.page_count == 0

    def test_full_response(self):
        response = ProcessResponse(
            claim_id="CLM002",
            status="success",
            documents=DocumentInfo(
                page_classification=[
                    PageClassification(page_number=1, document_type="identity_document", confidence=0.95),
                    PageClassification(page_number=2, document_type="discharge_summary", confidence=0.88),
                ],
                routing=RoutingMap(
                    id_agent_pages=[1],
                    discharge_summary_pages=[2],
                    itemized_bill_pages=[],
                ),
            ),
            extracted_data=ExtractedData(
                identity=IdentityData(
                    patient_name="John Doe",
                    date_of_birth="1990-01-15",
                    id_numbers=["ID123456"],
                    policy_details=PolicyDetails(
                        policy_number="POL789",
                        insurer="TestInsurer",
                        plan_name="Gold Plan",
                    ),
                ),
                discharge_summary=DischargeSummaryData(
                    diagnosis=["Appendicitis"],
                    admission_date="2024-01-10",
                    discharge_date="2024-01-12",
                    physicians=["Dr. Smith"],
                ),
                itemized_bill=ItemizedBillData(
                    items=[
                        BillItem(description="Room", quantity=2, unit_price=500, amount=1000),
                    ],
                    reported_total=1000.0,
                    calculated_total=1000.0,
                    currency="USD",
                ),
            ),
            validation=Validation(total_consistency_check=True, notes=[]),
            metadata=ProcessingMetadata(page_count=2, ocr_pages=[1], processing_time_ms=1234.56),
        )
        data = response.model_dump()
        assert data["claim_id"] == "CLM002"
        assert len(data["documents"]["page_classification"]) == 2
        assert data["extracted_data"]["identity"]["patient_name"] == "John Doe"
        assert data["extracted_data"]["itemized_bill"]["items"][0]["amount"] == 1000
        assert data["validation"]["total_consistency_check"] is True
        assert data["metadata"]["ocr_pages"] == [1]

    def test_response_json_serialization(self):
        response = ProcessResponse(claim_id="CLM003")
        json_str = response.model_dump_json()
        assert '"claim_id":"CLM003"' in json_str.replace(" ", "")

    def test_default_values(self):
        response = ProcessResponse(claim_id="CLM004")
        assert response.extracted_data.identity.id_numbers == []
        assert response.extracted_data.discharge_summary.diagnosis == []
        assert response.extracted_data.itemized_bill.items == []
        assert response.validation.notes == []
        assert response.metadata.ocr_pages == []

    def test_page_classification_model(self):
        pc = PageClassification(page_number=1, document_type="itemized_bill", confidence=0.92)
        assert pc.page_number == 1
        assert pc.document_type == "itemized_bill"
        assert pc.confidence == 0.92

    def test_bill_item_model(self):
        item = BillItem(description="Surgery", quantity=1, unit_price=5000, amount=5000)
        assert item.description == "Surgery"
        assert item.amount == 5000

    def test_bill_item_all_none(self):
        item = BillItem()
        assert item.description is None
        assert item.quantity is None
        assert item.unit_price is None
        assert item.amount is None
