import { ProcessResponse } from "@/lib/types";

interface SummaryCardProps {
  data: ProcessResponse;
}

export default function SummaryCard({ data }: SummaryCardProps) {
  const timeSeconds = (data.metadata.processing_time_ms / 1000).toFixed(1);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">
            {data.title || "Untitled Document"}
          </h2>
          {data.document_type && (
            <span className="inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
              {data.document_type}
            </span>
          )}
        </div>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          {data.status}
        </span>
      </div>

      {/* Summary */}
      {data.summary && (
        <div>
          <h3 className="text-sm font-medium text-gray-600 mb-1">Summary</h3>
          <p className="text-sm text-gray-700 leading-relaxed">{data.summary}</p>
        </div>
      )}

      {/* Key Topics */}
      {data.key_topics.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-600 mb-2">Key Topics</h3>
          <div className="flex flex-wrap gap-1.5">
            {data.key_topics.map((topic, i) => (
              <span
                key={i}
                className="px-2.5 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Metadata */}
      <div className="pt-4 border-t border-gray-100">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <Stat label="Document ID" value={data.document_id} />
          <Stat label="Pages" value={data.metadata.page_count.toString()} />
          <Stat label="OCR Pages" value={data.metadata.ocr_pages.length.toString()} />
          <Stat label="Processing Time" value={`${timeSeconds}s`} />
        </div>
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
