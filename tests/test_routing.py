"""Unit tests for page routing logic."""

import pytest
from app.agents.segregator import DOC_TYPE_TO_AGENT, VALID_DOC_TYPES


def build_routing_from_classifications(classifications):
    """Replicate the routing logic from segregator for testing."""
    routing = {
        "id_agent_pages": [],
        "discharge_summary_pages": [],
        "itemized_bill_pages": [],
    }
    for c in classifications:
        agent_key = DOC_TYPE_TO_AGENT.get(c["document_type"])
        if agent_key:
            routing[agent_key].append(c["page_number"])
    return routing


class TestRoutingLogic:
    def test_identity_document_routes_to_id_agent(self):
        classifications = [
            {"page_number": 1, "document_type": "identity_document", "confidence": 0.95},
        ]
        routing = build_routing_from_classifications(classifications)
        assert 1 in routing["id_agent_pages"]
        assert 1 not in routing["discharge_summary_pages"]
        assert 1 not in routing["itemized_bill_pages"]

    def test_claim_forms_routes_to_id_agent(self):
        classifications = [
            {"page_number": 2, "document_type": "claim_forms", "confidence": 0.9},
        ]
        routing = build_routing_from_classifications(classifications)
        assert 2 in routing["id_agent_pages"]

    def test_discharge_summary_routes_correctly(self):
        classifications = [
            {"page_number": 3, "document_type": "discharge_summary", "confidence": 0.85},
        ]
        routing = build_routing_from_classifications(classifications)
        assert 3 in routing["discharge_summary_pages"]
        assert 3 not in routing["id_agent_pages"]

    def test_prescription_routes_to_discharge_agent(self):
        classifications = [
            {"page_number": 4, "document_type": "prescription", "confidence": 0.8},
        ]
        routing = build_routing_from_classifications(classifications)
        assert 4 in routing["discharge_summary_pages"]

    def test_itemized_bill_routes_correctly(self):
        classifications = [
            {"page_number": 5, "document_type": "itemized_bill", "confidence": 0.9},
        ]
        routing = build_routing_from_classifications(classifications)
        assert 5 in routing["itemized_bill_pages"]

    def test_cash_receipt_routes_to_bill_agent(self):
        classifications = [
            {"page_number": 6, "document_type": "cash_receipt", "confidence": 0.7},
        ]
        routing = build_routing_from_classifications(classifications)
        assert 6 in routing["itemized_bill_pages"]

    def test_other_type_not_routed(self):
        classifications = [
            {"page_number": 7, "document_type": "other", "confidence": 0.5},
        ]
        routing = build_routing_from_classifications(classifications)
        assert routing["id_agent_pages"] == []
        assert routing["discharge_summary_pages"] == []
        assert routing["itemized_bill_pages"] == []

    def test_multiple_pages_routing(self):
        classifications = [
            {"page_number": 1, "document_type": "identity_document", "confidence": 0.9},
            {"page_number": 2, "document_type": "claim_forms", "confidence": 0.8},
            {"page_number": 3, "document_type": "discharge_summary", "confidence": 0.85},
            {"page_number": 4, "document_type": "itemized_bill", "confidence": 0.9},
            {"page_number": 5, "document_type": "itemized_bill", "confidence": 0.88},
            {"page_number": 6, "document_type": "other", "confidence": 0.5},
        ]
        routing = build_routing_from_classifications(classifications)
        assert routing["id_agent_pages"] == [1, 2]
        assert routing["discharge_summary_pages"] == [3]
        assert routing["itemized_bill_pages"] == [4, 5]

    def test_all_valid_doc_types_covered(self):
        """Ensure every valid doc type either routes somewhere or is 'other'."""
        for doc_type in VALID_DOC_TYPES:
            if doc_type == "other":
                assert doc_type not in DOC_TYPE_TO_AGENT
            else:
                assert doc_type in DOC_TYPE_TO_AGENT, f"{doc_type} has no routing"

    def test_empty_classifications(self):
        routing = build_routing_from_classifications([])
        assert routing["id_agent_pages"] == []
        assert routing["discharge_summary_pages"] == []
        assert routing["itemized_bill_pages"] == []
