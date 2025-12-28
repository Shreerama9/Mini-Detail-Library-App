const API_URL = 'http://localhost:8000';

export async function fetchDetails() {
  const response = await fetch(`${API_URL}/details`);
  if (!response.ok) throw new Error('Failed to fetch details');
  return response.json();
}

export async function searchDetails(query) {
  const response = await fetch(`${API_URL}/details/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error('Failed to search details');
  return response.json();
}

export async function suggestDetail(context) {
  const response = await fetch(`${API_URL}/suggest-detail`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(context)
  });
  if (!response.ok) throw new Error('Failed to get suggestion');
  return response.json();
}
