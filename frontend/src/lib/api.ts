import { ProcessResponse } from "./types";

const API_BASE = "http://localhost:8000";

export async function processClaim(
  claimId: string,
  file: File
): Promise<ProcessResponse> {
  const formData = new FormData();
  formData.append("claim_id", claimId);
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/process`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    const data = await response.json();
    return data.status === "healthy";
  } catch {
    return false;
  }
}
