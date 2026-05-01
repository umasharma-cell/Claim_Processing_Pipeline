"use client";

import { useState, useCallback } from "react";
import { ProcessResponse } from "@/lib/types";
import { processClaim } from "@/lib/api";

type ProcessingState =
  | { status: "idle" }
  | { status: "processing" }
  | { status: "success"; data: ProcessResponse }
  | { status: "error"; message: string };

export function useClaimProcessor() {
  const [state, setState] = useState<ProcessingState>({ status: "idle" });

  const submitClaim = useCallback(async (claimId: string, file: File) => {
    setState({ status: "processing" });
    try {
      const data = await processClaim(claimId, file);
      setState({ status: "success", data });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "An unexpected error occurred.";
      setState({ status: "error", message });
    }
  }, []);

  const reset = useCallback(() => {
    setState({ status: "idle" });
  }, []);

  return { state, submitClaim, reset };
}
