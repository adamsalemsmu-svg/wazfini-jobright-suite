// frontend/src/lib/api.js
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export function setToken(token) {
  localStorage.setItem("token", token);
}

export function getToken() {
  return localStorage.getItem("token");
}

async function request(path, opts = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(opts.headers || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const api = {
  login: async (username, password) => {
    const body = new URLSearchParams({
      username: username.trim().toLowerCase(),
      password,
    }).toString();
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  jobs: () => request("/jobs"),
  search: (filters) =>
    request("/jobs/search", { method: "POST", body: JSON.stringify(filters) }),
  chat: (payload) =>
    request("/assistant/chat", { method: "POST", body: JSON.stringify(payload) }),
};
