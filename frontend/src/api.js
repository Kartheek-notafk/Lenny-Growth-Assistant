const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  health: () => request("/health"),
  newSession: () => request("/api/sessions", { method: "POST" }),
  sessionMessages: (sessionId) => request(`/api/sessions/${sessionId}/messages`),
  chat: (sessionId, message, skill) =>
    request("/api/chat", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, message, skill }),
    }),
};
