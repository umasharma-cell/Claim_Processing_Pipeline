import { ItemizedBillData, Validation } from "@/lib/types";

interface ItemizedBillSectionProps {
  data: ItemizedBillData;
  validation: Validation;
}

function formatCurrency(amount: number | null, currency: string | null): string {
  if (amount === null) return "—";
  return `${currency || "USD"} ${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function ItemizedBillSection({ data, validation }: ItemizedBillSectionProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Itemized Bill</h2>
        <ValidationBadge check={validation.total_consistency_check} />
      </div>

      {data.items.length === 0 ? (
        <p className="text-sm text-gray-500">No bill items found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 pr-4 font-medium text-gray-600">Description</th>
                <th className="text-right py-2 pr-4 font-medium text-gray-600">Qty</th>
                <th className="text-right py-2 pr-4 font-medium text-gray-600">Unit Price</th>
                <th className="text-right py-2 font-medium text-gray-600">Amount</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item, i) => (
                <tr key={i} className="border-b border-gray-100">
                  <td className="py-2.5 pr-4 text-gray-800">{item.description || "—"}</td>
                  <td className="py-2.5 pr-4 text-right text-gray-800 tabular-nums">{item.quantity ?? "—"}</td>
                  <td className="py-2.5 pr-4 text-right text-gray-800 tabular-nums">
                    {item.unit_price !== null ? item.unit_price.toLocaleString(undefined, { minimumFractionDigits: 2 }) : "—"}
                  </td>
                  <td className="py-2.5 text-right text-gray-800 tabular-nums">
                    {item.amount !== null ? item.amount.toLocaleString(undefined, { minimumFractionDigits: 2 }) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="border-t-2 border-gray-200">
                <td colSpan={3} className="py-2.5 pr-4 text-right text-sm font-medium text-gray-600">
                  Reported Total
                </td>
                <td className="py-2.5 text-right font-semibold text-gray-800 tabular-nums">
                  {formatCurrency(data.reported_total, data.currency)}
                </td>
              </tr>
              <tr>
                <td colSpan={3} className="py-2.5 pr-4 text-right text-sm font-medium text-gray-600">
                  Calculated Total
                </td>
                <td className="py-2.5 text-right font-semibold text-gray-800 tabular-nums">
                  {formatCurrency(data.calculated_total, data.currency)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}

      {validation.notes.length > 0 && (
        <div className="mt-4 pt-3 border-t border-gray-100">
          {validation.notes.map((note, i) => (
            <p key={i} className="text-xs text-amber-700 bg-amber-50 px-3 py-1.5 rounded mt-1">
              {note}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

function ValidationBadge({ check }: { check: boolean | null }) {
  if (check === null) {
    return <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-500">N/A</span>;
  }
  if (check) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700">
        <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
        Totals Match
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700">
      <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
      </svg>
      Mismatch
    </span>
  );
}
