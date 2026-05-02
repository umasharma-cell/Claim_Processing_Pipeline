"use client";

import { useState, useEffect } from "react";

const STAGES = [
  "Parsing PDF...",
  "Extracting text from pages...",
  "Analyzing document content...",
  "Generating summary...",
  "Identifying key topics...",
];

export default function ProcessingStatus() {
  const [elapsed, setElapsed] = useState(0);
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setElapsed((e) => e + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setStageIndex((i) => (i + 1) % STAGES.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const mins = Math.floor(elapsed / 60);
  const secs = elapsed % 60;

  return (
    <div className="w-full max-w-md mx-auto text-center space-y-6 py-12">
      {/* Spinner */}
      <div className="flex justify-center">
        <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
      </div>

      <div>
        <p className="text-lg font-medium text-gray-800">Analyzing your document</p>
        <p className="text-sm text-gray-500 mt-1">This may take up to a minute</p>
      </div>

      {/* Stage hint */}
      <p className="text-sm text-blue-600 font-medium animate-pulse">
        {STAGES[stageIndex]}
      </p>

      {/* Timer */}
      <p className="text-xs text-gray-400 tabular-nums">
        Elapsed: {mins > 0 ? `${mins}m ` : ""}
        {secs}s
      </p>
    </div>
  );
}
