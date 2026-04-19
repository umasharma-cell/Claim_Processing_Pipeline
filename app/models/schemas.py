"""Pydantic models for request/response schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


# ── Request ──────────────────────────────────────────────────────────────────

class ProcessRequest(BaseModel):
    claim_id: str


# ── Page-level models ────────────────────────────────────────────────────────

class PageClassification(BaseModel):
    page_number: int
    document_type: str
    confidence: float = 0.0
    rationale: Optional[str] = None


class RoutingMap(BaseModel):
    id_agent_pages: List[int] = Field(default_factory=list)
    discharge_summary_pages: List[int] = Field(default_factory=list)
    itemized_bill_pages: List[int] = Field(default_factory=list)


class DocumentInfo(BaseModel):
    page_classification: List[PageClassification] = Field(default_factory=list)
    routing: RoutingMap = Field(default_factory=RoutingMap)


# ── Extracted data models ────────────────────────────────────────────────────

class PolicyDetails(BaseModel):
    policy_number: Optional[str] = None
    insurer: Optional[str] = None
    plan_name: Optional[str] = None


class IdentityData(BaseModel):
    patient_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    id_numbers: List[str] = Field(default_factory=list)
    policy_details: PolicyDetails = Field(default_factory=PolicyDetails)


class DischargeSummaryData(BaseModel):
    diagnosis: List[str] = Field(default_factory=list)
    admission_date: Optional[str] = None
    discharge_date: Optional[str] = None
    physicians: List[str] = Field(default_factory=list)


class BillItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None


class ItemizedBillData(BaseModel):
    items: List[BillItem] = Field(default_factory=list)
    reported_total: Optional[float] = None
    calculated_total: Optional[float] = None
    currency: Optional[str] = None


class ExtractedData(BaseModel):
    identity: IdentityData = Field(default_factory=IdentityData)
    discharge_summary: DischargeSummaryData = Field(default_factory=DischargeSummaryData)
    itemized_bill: ItemizedBillData = Field(default_factory=ItemizedBillData)


# ── Validation & Metadata ───────────────────────────────────────────────────

class Validation(BaseModel):
    total_consistency_check: Optional[bool] = None
    notes: List[str] = Field(default_factory=list)


class ProcessingMetadata(BaseModel):
    page_count: int = 0
    ocr_pages: List[int] = Field(default_factory=list)
    processing_time_ms: float = 0


# ── Final response ───────────────────────────────────────────────────────────

class ProcessResponse(BaseModel):
    claim_id: str
    status: str = "success"
    documents: DocumentInfo = Field(default_factory=DocumentInfo)
    extracted_data: ExtractedData = Field(default_factory=ExtractedData)
    validation: Validation = Field(default_factory=Validation)
    metadata: ProcessingMetadata = Field(default_factory=ProcessingMetadata)
