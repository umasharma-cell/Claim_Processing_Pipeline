import { DischargeSummaryData } from "@/lib/types";

interface DischargeSummarySectionProps {
  data: DischargeSummaryData;
}

function Val({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm text-gray-800 mt-0.5">{value || "—"}</p>
    </div>
  );
}

export default function DischargeSummarySection({ data }: DischargeSummarySectionProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Discharge Summary</h2>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <Val label="Admission Date" value={data.admission_date} />
        <Val label="Discharge Date" value={data.discharge_date} />
      </div>

      {data.diagnosis.length > 0 && (
        <div className="mb-4">
          <p className="text-xs text-gray-500 mb-1">Diagnosis</p>
          <div className="flex flex-wrap gap-1.5">
            {data.diagnosis.map((d, i) => (
              <span key={i} className="px-2.5 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
                {d}
              </span>
            ))}
          </div>
        </div>
      )}

      {data.physicians.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-1">Physicians</p>
          <div className="flex flex-wrap gap-1.5">
            {data.physicians.map((p, i) => (
              <span key={i} className="px-2.5 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                {p}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
