const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export async function runResearch({ topic, location }) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45000);
  try {
    const response = await fetch(`${API_BASE_URL}/research`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: topic.trim(), location: location.trim() }), signal: controller.signal,
    });
    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      const detail = payload?.detail;
      throw new Error(typeof detail === 'string' ? detail : `Research request failed (${response.status}).`);
    }
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) throw new Error('The research engine returned an unexpected response.');
    return payload;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('The research request timed out. Please try again.');
    if (error instanceof TypeError) throw new Error('Unable to connect to the research engine. Please make sure the backend is running.');
    throw error;
  } finally { clearTimeout(timeout); }
}
