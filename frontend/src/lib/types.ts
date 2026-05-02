export interface ProcessingMetadata {
  page_count: number;
  ocr_pages: number[];
  processing_time_ms: number;
}

export interface ProcessResponse {
  document_id: string;
  status: string;
  title: string | null;
  summary: string | null;
  key_topics: string[];
  document_type: string | null;
  metadata: ProcessingMetadata;
}
