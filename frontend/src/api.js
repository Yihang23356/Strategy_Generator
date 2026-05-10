const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function parseResponse(response) {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `请求失败: ${response.status}`);
  }
  return response.json();
}

export async function runReviewUpload(formData) {
  const response = await fetch(`${API_BASE_URL}/api/review/run-upload`, {
    method: "POST",
    body: formData,
  });
  return parseResponse(response);
}

export async function getReviewRun(runId) {
  const response = await fetch(`${API_BASE_URL}/api/review/runs/${runId}`);
  return parseResponse(response);
}

export async function getBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return parseResponse(response);
}
