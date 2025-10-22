export const API_BASE =
  import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiGet(path: string) {
  const res = await fetch(`${API_BASE}${path}`, { headers: { ...authHeaders() } });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiPost(path: string, body: any, isForm = false) {
  const headers: Record<string, string> = { ...authHeaders() };
  if (!isForm) headers["Content-Type"] = "application/json";
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: isForm ? body : JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function uploadResumeFile(file: File) {
  const form = new FormData();
  form.append("file", file);
  return apiPost("/upload/resume", form, true);
}

export async function penguinChat(message: string, job_id?: number) {
  return apiPost("/assistant/chat", { job_id, question: message, use_active_resume: true });
}
