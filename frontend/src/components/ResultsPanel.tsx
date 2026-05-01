import { ProcessResponse } from "@/lib/types";
import SummaryCard from "./SummaryCard";
import PageClassifications from "./PageClassifications";
import IdentitySection from "./IdentitySection";
import DischargeSummarySection from "./DischargeSummarySection";
import ItemizedBillSection from "./ItemizedBillSection";

interface ResultsPanelProps {
  data: ProcessResponse;
  onReset: () => void;
}

export default function ResultsPanel({ data, onReset }: ResultsPanelProps) {
  return (
    <div className="w-full max-w-3xl mx-auto space-y-6">
      <SummaryCard data={data} />
      <PageClassifications documents={data.documents} />
      <IdentitySection data={data.extracted_data.identity} />
      <DischargeSummarySection data={data.extracted_data.discharge_summary} />
      <ItemizedBillSection
        data={data.extracted_data.itemized_bill}
        validation={data.validation}
      />

      <div className="text-center pt-4">
        <button
          onClick={onReset}
          className="px-6 py-2.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
        >
          Process Another Claim
        </button>
      </div>
    </div>
  );
}
