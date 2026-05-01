"use client";

import { useClaimProcessor } from "@/hooks/useClaimProcessor";
import UploadForm from "@/components/UploadForm";
import ProcessingStatus from "@/components/ProcessingStatus";
import ResultsPanel from "@/components/ResultsPanel";
import ErrorDisplay from "@/components/ErrorDisplay";

export default function Home() {
  const { state, submitClaim, reset } = useClaimProcessor();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Claim Processing Pipeline</h1>
            <p className="text-xs text-gray-500">AI-powered document extraction</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-8">
        {state.status === "idle" && (
          <div className="flex flex-col items-center pt-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Process a Claim Document</h2>
            <p className="text-sm text-gray-500 mb-8">Upload a PDF to extract identity, discharge summary, and billing information</p>
            <UploadForm onSubmit={submitClaim} />
          </div>
        )}

        {state.status === "processing" && <ProcessingStatus />}

        {state.status === "success" && (
          <ResultsPanel data={state.data} onReset={reset} />
        )}

        {state.status === "error" && (
          <ErrorDisplay message={state.message} onRetry={reset} />
        )}
      </main>
    </div>
  );
}
