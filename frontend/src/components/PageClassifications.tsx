import { DocumentInfo } from "@/lib/types";

interface PageClassificationsProps {
  documents: DocumentInfo;
}

function formatDocType(type: string): string {
  return type
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function confidenceColor(c: number): string {
  if (c >= 0.8) return "bg-green-500";
  if (c >= 0.5) return "bg-yellow-500";
  return "bg-red-500";
}

export default function PageClassifications({ documents }: PageClassificationsProps) {
  const { page_classification, routing } = documents;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Page Classifications</h2>

      {page_classification.length === 0 ? (
        <p className="text-sm text-gray-500">No pages classified.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 pr-4 font-medium text-gray-600">Page</th>
                <th className="text-left py-2 pr-4 font-medium text-gray-600">Document Type</th>
                <th className="text-left py-2 pr-4 font-medium text-gray-600">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {page_classification.map((pc) => (
                <tr key={pc.page_number} className="border-b border-gray-100">
                  <td className="py-2.5 pr-4 text-gray-800">{pc.page_number}</td>
                  <td className="py-2.5 pr-4 text-gray-800">{formatDocType(pc.document_type)}</td>
                  <td className="py-2.5 pr-4">
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${confidenceColor(pc.confidence)}`}
                          style={{ width: `${pc.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 tabular-nums">
                        {(pc.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Routing Summary */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <p className="text-xs font-medium text-gray-500 mb-2">Agent Routing</p>
        <div className="flex flex-wrap gap-2 text-xs">
          {routing.id_agent_pages.length > 0 && (
            <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded">
              ID Agent: pages {routing.id_agent_pages.join(", ")}
            </span>
          )}
          {routing.discharge_summary_pages.length > 0 && (
            <span className="px-2 py-1 bg-teal-50 text-teal-700 rounded">
              Discharge: pages {routing.discharge_summary_pages.join(", ")}
            </span>
          )}
          {routing.itemized_bill_pages.length > 0 && (
            <span className="px-2 py-1 bg-orange-50 text-orange-700 rounded">
              Bill: pages {routing.itemized_bill_pages.join(", ")}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
