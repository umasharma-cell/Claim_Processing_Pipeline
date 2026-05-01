import { ProcessResponse } from "@/lib/types";

interface SummaryCardProps {
  data: ProcessResponse;
}

export default function SummaryCard({ data }: SummaryCardProps) {
  const timeSeconds = (data.metadata.processing_time_ms / 1000).toFixed(1);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Claim Summary</h2>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          {data.status}
        </span>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Stat label="Claim ID" value={data.claim_id} />
        <Stat label="Pages" value={data.metadata.page_count.toString()} />
        <Stat label="OCR Pages" value={data.metadata.ocr_pages.length.toString()} />
        <Stat label="Processing Time" value={`${timeSeconds}s`} />
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-semibold text-gray-800 mt-0.5">{value}</p>
    </div>
  );
}
