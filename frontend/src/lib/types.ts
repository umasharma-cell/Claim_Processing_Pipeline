export interface PageClassification {
  page_number: number;
  document_type: string;
  confidence: number;
  rationale?: string | null;
}

export interface RoutingMap {
  id_agent_pages: number[];
  discharge_summary_pages: number[];
  itemized_bill_pages: number[];
}

export interface DocumentInfo {
  page_classification: PageClassification[];
  routing: RoutingMap;
}

export interface PolicyDetails {
  policy_number: string | null;
  insurer: string | null;
  plan_name: string | null;
}

export interface IdentityData {
  patient_name: string | null;
  date_of_birth: string | null;
  id_numbers: string[];
  policy_details: PolicyDetails;
}

export interface DischargeSummaryData {
  diagnosis: string[];
  admission_date: string | null;
  discharge_date: string | null;
  physicians: string[];
}

export interface BillItem {
  description: string | null;
  quantity: number | null;
  unit_price: number | null;
  amount: number | null;
}

export interface ItemizedBillData {
  items: BillItem[];
  reported_total: number | null;
  calculated_total: number | null;
  currency: string | null;
}

export interface ExtractedData {
  identity: IdentityData;
  discharge_summary: DischargeSummaryData;
  itemized_bill: ItemizedBillData;
}

export interface Validation {
  total_consistency_check: boolean | null;
  notes: string[];
}

export interface ProcessingMetadata {
  page_count: number;
  ocr_pages: number[];
  processing_time_ms: number;
}

export interface ProcessResponse {
  claim_id: string;
  status: string;
  documents: DocumentInfo;
  extracted_data: ExtractedData;
  validation: Validation;
  metadata: ProcessingMetadata;
}
