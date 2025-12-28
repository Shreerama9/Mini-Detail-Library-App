const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(message, status, type = 'unknown') {
    super(message);
    this.status = status;
    this.type = type;
  }
}

async function handleResponse(response) {
  if (!response.ok) {
    const type = response.status >= 500 ? 'server' : 'client';
    throw new ApiError(
      `API Error: ${response.status} ${response.statusText}`,
      response.status,
      type
    );
  }
  return response.json();
}

async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, options);
    return handleResponse(response);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError('Network error. Is the backend running?', 0, 'network');
  }
}

export async function fetchDetails() {
  return apiRequest(`${API_URL}/details`);
}

export async function searchDetails(query) {
  return apiRequest(`${API_URL}/details/search?q=${encodeURIComponent(query)}`);
}

export async function suggestDetail(context) {
  return apiRequest(`${API_URL}/suggest-detail-rag`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(context)
  });
}

export async function autocomplete(query) {
  try {
    return await apiRequest(`${API_URL}/details/autocomplete?q=${encodeURIComponent(query)}`);
  } catch {
    return { suggestions: [] };
  }
}

export async function fetchSecureDetails(role) {
  return apiRequest(`${API_URL}/secure/details`, {
    headers: {
      'X-User-Role': role,
      'X-User-Email': `${role}@piaxis.com`
    }
  });
}

export async function generateEmbeddings() {
  return apiRequest(`${API_URL}/generate-embeddings`, {
    method: 'POST'
  });
}
