import { IdentityData } from "@/lib/types";

interface IdentitySectionProps {
  data: IdentityData;
}

function Val({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm text-gray-800 mt-0.5">{value || "—"}</p>
    </div>
  );
}

export default function IdentitySection({ data }: IdentitySectionProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Patient Identity</h2>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <Val label="Patient Name" value={data.patient_name} />
        <Val label="Date of Birth" value={data.date_of_birth} />
      </div>

      {data.id_numbers.length > 0 && (
        <div className="mb-4">
          <p className="text-xs text-gray-500 mb-1">ID Numbers</p>
          <div className="flex flex-wrap gap-1.5">
            {data.id_numbers.map((id, i) => (
              <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">
                {id}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Policy Details */}
      <div className="pt-4 border-t border-gray-100">
        <p className="text-xs font-medium text-gray-500 mb-3">Policy Details</p>
        <div className="grid grid-cols-3 gap-4">
          <Val label="Policy Number" value={data.policy_details.policy_number} />
          <Val label="Insurer" value={data.policy_details.insurer} />
          <Val label="Plan Name" value={data.policy_details.plan_name} />
        </div>
      </div>
    </div>
  );
}
