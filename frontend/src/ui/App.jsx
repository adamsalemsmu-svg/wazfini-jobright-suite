// frontend/ui/App.jsx
import React, { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

/* ── AUTH ─────────────────────────────────────────────────────────── */
function useAuth() {
  const [token, setToken] = useState(() => localStorage.getItem("token") || "");
  const [me, setMe] = useState(null);

  useEffect(() => {
    if (!token) return setMe(null);
    fetch(`${API_BASE}/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => (r.ok ? r.json() : null))
      .then(setMe)
      .catch(() => setMe(null));
  }, [token]);

  const login = async (email, password) => {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });
    if (!res.ok) {
      let msg = "Invalid credentials";
      try { msg = (await res.json()).detail || msg; } catch {}
      throw new Error(msg);
    }
    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);
  };

  const register = async (name, email, password) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Register failed");
    return login(email, password);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken("");
    setMe(null);
  };

  return { token, me, login, register, logout };
}

/* ── THEME ─────────────────────────────────────────────────────────── */
function DarkToggle() {
  const [enabled, setEnabled] = useState(() =>
    document.documentElement.classList.contains("dark")
  );
  useEffect(() => {
    const root = document.documentElement;
    if (enabled) root.classList.add("dark");
    else root.classList.remove("dark");
  }, [enabled]);
  return (
    <button
      onClick={() => setEnabled((v) => !v)}
      className="rounded-xl px-3 py-2 border text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800"
      title="Toggle theme"
    >
      {enabled ? "🌙 Dark" : "☀️ Light"}
    </button>
  );
}

/* ── AUTH PANEL ────────────────────────────────────────────────────── */
function AuthPanel({ onLogin, onRegister }) {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      if (mode === "login") await onLogin(email, password);
      else await onRegister(name, email, password);
    } catch (ex) {
      setErr(ex.message || "Something went wrong");
    }
  };

  return (
    <div className="max-w-sm w-full mx-auto mt-16 p-6 rounded-2xl border bg-white dark:bg-neutral-900 dark:border-neutral-800">
      <h1 className="text-xl font-semibold mb-2">
        {mode === "login" ? "Welcome back" : "Create your account"}
      </h1>
      <p className="text-sm text-neutral-500 mb-4">
        Sign {mode === "login" ? "in" : "up"} to manage jobs & resumes.
      </p>
      {err && <div className="mb-3 text-red-600 text-sm">{err}</div>}
      <form onSubmit={submit} className="space-y-3">
        {mode === "register" && (
          <input
            className="w-full border rounded-lg px-3 py-2 dark:bg-neutral-900 dark:border-neutral-700"
            placeholder="Full name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        )}
        <input
          className="w-full border rounded-lg px-3 py-2 dark:bg-neutral-900 dark:border-neutral-700"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          className="w-full border rounded-lg px-3 py-2 dark:bg-neutral-900 dark:border-neutral-700"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          className="w-full rounded-lg px-3 py-2 bg-black text-white dark:bg-white dark:text-black"
          type="submit"
        >
          {mode === "login" ? "Sign in" : "Sign up"}
        </button>
      </form>
      <div className="text-sm mt-4 text-center">
        {mode === "login" ? (
          <>No account? <button className="underline" onClick={() => setMode("register")}>Create one</button></>
        ) : (
          <>Already have an account? <button className="underline" onClick={() => setMode("login")}>Sign in</button></>
        )}
      </div>
    </div>
  );
}

/* ── RESUMES & TAILOR ──────────────────────────────────────────────── */
function ResumeEditor({ token, onSaved, initial }) {
  const [title, setTitle] = useState(initial?.title || "");
  const [content, setContent] = useState(initial?.content || "");
  const [saving, setSaving] = useState(false);
  const isEdit = Boolean(initial?.id);

  const save = async () => {
    setSaving(true);
    const url = isEdit ? `${API_BASE}/resumes/${initial.id}` : `${API_BASE}/resumes`;
    const method = isEdit ? "PUT" : "POST";
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ title, content }),
    });
    setSaving(false);
    if (!res.ok) { alert("Save failed"); return; }
    onSaved(await res.json());
  };

  return (
    <div className="space-y-2">
      <input
        className="w-full border rounded-lg px-3 py-2 dark:bg-neutral-900 dark:border-neutral-700"
        placeholder="Resume title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <textarea
        className="w-full h-56 border rounded-lg px-3 py-2 dark:bg-neutral-900 dark:border-neutral-700"
        placeholder="Paste your resume text/markdown..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />
      <button
        onClick={save}
        disabled={saving}
        className="rounded-lg px-3 py-2 bg-black text-white dark:bg-white dark:text-black disabled:opacity-60"
      >
        {saving ? "Saving..." : isEdit ? "Update" : "Create"}
      </button>
    </div>
  );
}

function TailorPanel({ token, resumes, onCreate }) {
  const [baseId, setBaseId] = useState(resumes[0]?.id || null);
  const [jd, setJd] = useState("");
  const [roleTitle, setRoleTitle] = useState("Tailored Resume");
  const [style, setStyle] = useState("Action-oriented, quantified, ATS-friendly, concise.");
  const [out, setOut] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => { if (!baseId && resumes.length) setBaseId(resumes[0].id); }, [resumes]);

  const run = async () => {
    if (!baseId || !jd.trim()) return;
    setLoading(true); setOut("");
    const res = await fetch(`${API_BASE}/tailor`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ resume_id: baseId, job_description: jd, role_title: roleTitle, style }),
    });
    setLoading(false);
    if (!res.ok) { alert("Tailor failed: " + (await res.text())); return; }
    const data = await res.json();
    setOut(data.tailored_content);
  };

  const saveAsNew = async () => {
    if (!out.trim()) return;
    const res = await fetch(`${API_BASE}/resumes`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ title: roleTitle || "Tailored Resume", content: out }),
    });
    if (!res.ok) { alert("Save failed"); return; }
    const created = await res.json();
    onCreate(created);
    alert("Saved as new resume!");
  };

  return (
    <div className="p-4 rounded-2xl border bg-white dark:bg-neutral-900 dark:border-neutral-800">
      <h2 className="font-medium mb-3">Tailor Resume (AI)</h2>
      <div className="space-y-2">
        <label className="text-sm">Base resume</label>
        <select
          className="w-full border rounded-lg px-3 py-2 dark:bg-neutral-900 dark:border-neutral-700"
          value={baseId || ""}
          onChange={(e) => setBaseId(Number(e.target.value))}
        >
          {resumes.map((r) => <option key={r.id} value={r.id}>{r.title}</option>)}
        </select>

        <input
          className="w-full border rounded-lg px-3 py-2 dark:bg-neutral-900 dark:border-neutral-700"
          placeholder="Title for the tailored resume (e.g., Senior Data Engineer @ Company)"
          value={roleTitle}
          onChange={(e) => setRoleTitle(e.target.value)}
        />

        <textarea
          className="w-full h-40 border rounded-lg px-3 py-2 dark:bg-neutral-900 dark:border-neutral-700"
          placeholder="Paste the job description here…"
          value={jd}
          onChange={(e) => setJd(e.target.value)}
        />

        <div className="flex gap-2 flex-wrap">
          <button
            onClick={run}
            disabled={loading || !baseId || !jd.trim()}
            className="rounded-lg px-3 py-2 bg-black text-white dark:bg-white dark:text-black disabled:opacity-60"
          >
            {loading ? "Tailoring…" : "Generate Tailored Resume"}
          </button>
          <button
            onClick={saveAsNew}
            disabled={!out.trim()}
            className="rounded-lg px-3 py-2 border dark:border-neutral-700"
          >
            Save as New Resume
          </button>
        </div>

        <div>
          <h3 className="mt-4 font-medium">Preview</h3>
          <pre className="whitespace-pre-wrap text-sm mt-2 text-neutral-700 dark:text-neutral-300">
            {out || "— Tailored content will appear here —"}
          </pre>
        </div>
      </div>
    </div>
  );
}

function ResumePage({ me, token, onLogout }) {
  const [resumes, setResumes] = useState([]);
  const [editing, setEditing] = useState(null);
  const headers = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  const load = async () => {
    const res = await fetch(`${API_BASE}/resumes`, { headers });
    if (!res.ok) return;
    setResumes(await res.json());
  };
  useEffect(() => { load(); }, []);

  const remove = async (id) => {
    if (!confirm("Delete this resume?")) return;
    const res = await fetch(`${API_BASE}/resumes/${id}`, { method: "DELETE", headers });
    if (res.status === 204) setResumes((arr) => arr.filter((r) => r.id !== id));
  };

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold">Resume Library</h1>
          <p className="text-sm text-neutral-500">Signed in as <b>{me.email}</b></p>
        </div>
        <div className="flex items-center gap-2">
          <DarkToggle />
          <button onClick={onLogout} className="rounded-xl px-3 py-2 border text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800">Logout</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 p-4 rounded-2xl border bg-white dark:bg-neutral-900 dark:border-neutral-800">
          <h2 className="font-medium mb-3">{editing ? "Edit Resume" : "New Resume"}</h2>
          <ResumeEditor
            token={token}
            initial={editing}
            onSaved={(r) => {
              setEditing(null);
              setResumes((arr) => {
                const idx = arr.findIndex((x) => x.id === r.id);
                if (idx >= 0) { const copy = arr.slice(); copy[idx] = r; return copy; }
                return [r, ...arr];
              });
            }}
          />
        </div>

        <div className="lg:col-span-1 p-4 rounded-2xl border bg-white dark:bg-neutral-900 dark:border-neutral-800">
          <h2 className="font-medium mb-3">Saved Resumes</h2>
          <ul className="space-y-3">
            {resumes.map((r) => (
              <li key={r.id} className="rounded-xl border p-3 dark:border-neutral-800">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{r.title}</div>
                    <div className="text-xs text-neutral-500">Updated {new Date(r.updated_at).toLocaleString()}</div>
                  </div>
                  <div className="flex gap-2">
                    <button className="text-sm underline" onClick={() => setEditing(r)}>Edit</button>
                    <button className="text-sm underline text-red-600" onClick={() => remove(r.id)}>Delete</button>
                  </div>
                </div>
                <pre className="whitespace-pre-wrap text-sm mt-2 text-neutral-700 dark:text-neutral-300">
                  {r.content.slice(0, 400)}{r.content.length > 400 ? "…" : ""}
                </pre>
              </li>
            ))}
          </ul>
        </div>

        <div className="lg:col-span-1">
          <TailorPanel token={token} resumes={resumes} onCreate={(created) => setResumes((arr) => [created, ...arr])} />
        </div>
      </div>
    </div>
  );
}

/* ── JOBS ──────────────────────────────────────────────────────────── */
const DEFAULT_TAGS = [
  "Data Engineer","Business/BI Analyst","Data Scientist",
  "Healthcare Data Scientist","Business Analyst","Power BI Developer",
  "ETL Developer","Data Analyst","AI Engineer"
];

const DEMO_JOBS = [
  { id:"cap1", company:"Capital One", logo:"🏦", title:"Sr. Data Analyst – Enterprise Services",
    location:"McLean, VA", mode:"Onsite", posted:"1 hour ago", salary:"$99k/yr – $113k/yr",
    seniority:"Mid, Senior Level", exp:"2+ years exp", match:98,
    perks:["Comp. & Benefits","H1B Sponsored"], applicants:"< 25 applicants", url:"https://www.capitalonecareers.com" },
  { id:"cap2", company:"Capital One", logo:"🏦", title:"Manager, Data Analysis – Card Services",
    location:"McLean, VA", mode:"Onsite", posted:"1 hour ago", salary:"$158k/yr – $181k/yr",
    seniority:"Mid, Senior Level", exp:"6+ years exp", match:94,
    perks:["Comp. & Benefits","H1B Sponsored"], applicants:"< 25 applicants", url:"https://www.capitalonecareers.com" },
  { id:"temu1", company:"Temu", logo:"🛒", title:"Data Engineer",
    location:"United States", mode:"Remote", posted:"5 hours ago", salary:"$100k/yr – $300k/yr",
    seniority:"Mid Level", exp:"3+ years exp", match:98,
    perks:["H1B Sponsor Likely"], applicants:"200+ applicants", url:"https://www.temu.com" }
];

function usePersistedSet(key) {
  const [set, setSet] = useState(() => new Set(JSON.parse(localStorage.getItem(key) || "[]")));
  useEffect(() => { localStorage.setItem(key, JSON.stringify([...set])); }, [set]);
  const toggle = (id) => setSet((prev) => { const next = new Set(prev); next.has(id) ? next.delete(id) : next.add(id); return next; });
  const has = (id) => set.has(id);
  return { set, toggle, has };
}

function Chip({ text, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1 rounded-full text-sm border transition ${
        active ? "bg-black text-white dark:bg-white dark:text-black"
               : "hover:bg-neutral-100 dark:hover:bg-neutral-800"
      }`}
    >
      {text}
    </button>
  );
}

function Badge({ children }) {
  return <span className="inline-flex items-center gap-1 rounded-full text-xs px-2 py-1 border dark:border-neutral-700">{children}</span>;
}

function MatchPill({ percent, labels = [] }) {
  return (
    <div className="w-full sm:w-[140px] md:w-[160px] rounded-2xl border p-3 text-center bg-white dark:bg-neutral-900 dark:border-neutral-700">
      <div className="text-2xl md:text-3xl font-semibold">{percent}%</div>
      <div className="text-[10px] md:text-xs text-neutral-500 mt-1">STRONG MATCH</div>
      <div className="mt-2 space-y-1 hidden md:block">
        {labels.map((l, i) => (<div key={i} className="text-xs">✓ {l}</div>))}
      </div>
    </div>
  );
}

function JobCard({ job, onDetails, onLike, onSave, onApply, liked, saved, applied, onAutofill }) {
  return (
    <div className="rounded-2xl border p-4 bg-white dark:bg-neutral-900 dark:border-neutral-800">
      <div className="flex flex-col md:flex-row gap-4">
        <div className="text-3xl">{job.logo}</div>
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <div className="text-xs text-neutral-500">{job.posted}</div>
            <Badge>Be an early applicant</Badge>
          </div>
          <div className="mt-1 font-semibold">{job.title}</div>
          <div className="text-sm text-neutral-600 dark:text-neutral-300">{job.company} • {job.location}</div>
          <div className="flex flex-wrap items-center gap-3 text-xs text-neutral-500 mt-2">
            <div>🏢 {job.mode}</div>
            <div>💵 {job.salary}</div>
            <div>📈 {job.seniority}</div>
            <div>⏳ {job.exp}</div>
            <div>{job.applicants}</div>
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <button onClick={onLike} className={`rounded-full px-3 py-2 border text-sm ${liked ? "bg-rose-500 text-white" : "hover:bg-neutral-100 dark:hover:bg-neutral-800"}`}>{liked ? "Liked ❤️" : "Like ❤️"}</button>
            <button onClick={onSave} className={`rounded-full px-3 py-2 border text-sm ${saved ? "bg-amber-500 text-white" : "hover:bg-neutral-100 dark:hover:bg-neutral-800"}`}>{saved ? "Saved 🔖" : "Save 🔖"}</button>
            <button onClick={onApply} className={`rounded-full px-3 py-2 text-sm ${applied ? "bg-emerald-700 text-white" : "bg-emerald-500 text-white"} hover:brightness-95`}>{applied ? "Applied ✅" : "Apply Now"}</button>
            <button onClick={onAutofill} className="rounded-full px-3 py-2 border text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800">Greenhouse Autofill</button>
            <button onClick={onDetails} className="rounded-full px-3 py-2 border text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800">Details</button>
          </div>
        </div>
        <MatchPill percent={job.match} labels={job.perks} />
      </div>
    </div>
  );
}

function JobDetailsDrawer({ job, open, onClose, onLike, onSave, onApply, liked, saved, applied, onAutofill }) {
  if (!open || !job) return null;
  return (
    <div className="fixed inset-0 z-40">
      <div className="absolute inset-0 bg-black/40" onClick={onClose}></div>
      <div className="absolute right-0 top-0 h-full w-full sm:max-w-md lg:max-w-xl xl:max-w-2xl bg-white dark:bg-neutral-900 border-l dark:border-neutral-800 p-5 overflow-y-auto">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="text-3xl">{job.logo}</div>
            <div>
              <div className="font-semibold">{job.title}</div>
              <div className="text-sm text-neutral-500">{job.company} • {job.location}</div>
            </div>
          </div>
          <button onClick={onClose} className="rounded-full px-3 py-1 border">✖</button>
        </div>
        <div className="flex gap-2 mb-3">
          <Badge>Posted {job.posted}</Badge>
          <Badge>{job.mode}</Badge>
          <Badge>{job.seniority}</Badge>
          <Badge>{job.exp}</Badge>
        </div>
        <div className="mb-4 text-sm text-neutral-600 dark:text-neutral-300">
          <p>Estimated salary: {job.salary}. Applicants: {job.applicants}.</p>
          <p className="mt-2">Responsibilities: Build ELT pipelines, model data for BI, and deliver dashboards.
            Stack: SQL, Python, dbt, Snowflake, Power BI/Tableau, ADF/Databricks.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={onLike} className={`rounded-full px-3 py-2 border text-sm ${liked ? "bg-rose-500 text-white" : "hover:bg-neutral-100 dark:hover:bg-neutral-800"}`}>{liked ? "Liked ❤️" : "Like ❤️"}</button>
          <button onClick={onSave} className={`rounded-full px-3 py-2 border text-sm ${saved ? "bg-amber-500 text-white" : "hover:bg-neutral-100 dark:hover:bg-neutral-800"}`}>{saved ? "Saved 🔖" : "Save 🔖"}</button>
          <button onClick={onApply} className={`rounded-full px-3 py-2 text-sm ${applied ? "bg-emerald-700 text-white" : "bg-emerald-500 text-white"} hover:brightness-95`}>{applied ? "Applied ✅" : "Apply Now"}</button>
          <button onClick={onAutofill} className="rounded-full px-3 py-2 border text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800">Greenhouse Autofill</button>
          <a target="_blank" href={job.url} className="rounded-full px-3 py-2 border text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800">Open posting ↗</a>
        </div>
      </div>
    </div>
  );
}

function RightCopilot({ me, selectedJob, token, resumes }) {
  const [q, setQ] = useState("");
  const [msgs, setMsgs] = useState([
    { role: "system", content: `Welcome back, ${me?.name || me?.email}! Ask about the selected job and how to tune your resume.` }
  ]);
  const hasResume = resumes?.length > 0;

  const ask = async () => {
    if (!q.trim()) return;
    const userMsg = { role: "user", content: q };
    setMsgs((m) => [...m, userMsg]);

    if (token && hasResume) {
      const resume = resumes[0];
      try {
        const res = await fetch(`${API_BASE}/tailor`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({
            resume_content: `${resume.content}\n\n[Question]: ${q}\n[Context]: Job: ${selectedJob ? selectedJob.title + " @ " + selectedJob.company : "N/A"}`,
            job_description: selectedJob ? `${selectedJob.title} at ${selectedJob.company}. ${selectedJob.seniority}. ${selectedJob.exp}. ${selectedJob.salary}.` : q,
            role_title: "Advice",
            style: "Give concrete, bullet-point advice; ATS-friendly; add keywords."
          })
        });
        if (res.ok) {
          const data = await res.json();
          setMsgs((m) => [...m, { role: "assistant", content: data.tailored_content }]);
          setQ(""); return;
        }
      } catch {}
    }
    const tip = [
      "• Mirror JD keywords in your top 5 bullets.",
      "• Quantify outcomes (%, $, time saved).",
      "• Put the stack first: SQL, Python, Snowflake, dbt, ADF/Databricks.",
      "• Keep bullets 1–2 lines each; no paragraphs."
    ].join("\n");
    setMsgs((m) => [...m, { role: "assistant", content: tip }]);
    setQ("");
  };

  return (
    <div className="rounded-2xl border p-4 bg-white dark:bg-neutral-900 dark:border-neutral-800 flex flex-col h-full sticky top-4">
      <div className="font-semibold">Penguin (AI Assistant)</div>
      <div className="text-xs text-neutral-500">Ask about the selected job & how to tune your resume.</div>
      <div className="mt-3 text-sm">
        {selectedJob ? <>Selected: <b>{selectedJob.title}</b> • {selectedJob.company}</> : "Select a job to get context-aware tips."}
      </div>
      <div className="mt-3 space-y-2 flex-1 overflow-auto">
        {msgs.map((m, i) => (
          <div key={i} className={`text-sm ${m.role === "assistant" ? "text-neutral-100 bg-neutral-800 p-2 rounded-lg" : ""}`}>
            {m.content}
          </div>
        ))}
      </div>
      <div className="mt-2 flex gap-2">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ask about this job or your resume…" className="flex-1 border rounded-xl px-3 py-2 dark:bg-neutral-900 dark:border-neutral-700" />
        <button onClick={ask} className="rounded-xl px-3 py-2 bg-emerald-500 text-white">Ask</button>
      </div>
    </div>
  );
}

function JobsPage({ me, token }) {
  const [tab, setTab] = useState("Recommended");
  const [activeTags, setActiveTags] = useState(new Set(["Data Engineer","Business/BI Analyst"]));
  const [query, setQuery] = useState("");
  const [drawerJob, setDrawerJob] = useState(null);

  const { set: liked, toggle: toggleLike, has: isLiked } = usePersistedSet("likedJobs");
  const { set: saved, toggle: toggleSave, has: isSaved } = usePersistedSet("savedJobs");
  const { set: applied, toggle: toggleApply, has: isApplied } = usePersistedSet("appliedJobs");

  const [resumes, setResumes] = useState([]);
  useEffect(() => {
    if (!token) return;
    fetch(`${API_BASE}/resumes`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => (r.ok ? r.json() : []))
      .then(setResumes)
      .catch(() => setResumes([]));
  }, [token]);

  const toggleTag = (t) => setActiveTags((prev) => { const next = new Set(prev); next.has(t) ? next.delete(t) : next.add(t); return next; });
  const matchesQuery = (j) => j.title.toLowerCase().includes(query.toLowerCase()) || j.company.toLowerCase().includes(query.toLowerCase());
  const filtered = DEMO_JOBS.filter(matchesQuery);
  const tabFilter = (j) => tab==="Liked" ? isLiked(j.id) : tab==="Applied" ? isApplied(j.id) : tab==="External" ? j.mode==="Remote" : true;

  const onAutofill = async (job) => {
    try {
      const res = await fetch(`${API_BASE}/autofill/greenhouse`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ job_url: job.url, mapping: "profile->form" })
      });
      if (!res.ok) throw new Error("No endpoint (stub).");
      alert("Autofill request queued!");
    } catch {
      window.open(job.url, "_blank", "noopener");
    }
  };

  return (
    <div className="container py-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="text-2xl font-bold">JOBS</div>
          <div className="flex gap-1 ml-3">
            {["Recommended","Liked","Applied","External"].map((t) => (
              <button key={t} onClick={() => setTab(t)}
                className={`rounded-full px-3 py-1 text-sm border ${tab===t ? "bg-black text-white dark:bg-white dark:text-black" : "hover:bg-neutral-100 dark:hover:bg-neutral-800"}`}>
                {t}
              </button>
            ))}
          </div>
        </div>
        <DarkToggle />
      </div>

      {/* Filters + Search */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <div className="flex flex-wrap gap-2">
          {DEFAULT_TAGS.map((t) => <Chip key={t} text={t} active={activeTags.has(t)} onClick={() => toggleTag(t)} />)}
          <button className="px-3 py-1 rounded-full text-sm border hover:bg-neutral-100 dark:hover:bg-neutral-800">+29</button>
          <button className="px-3 py-1 rounded-full text-sm bg-emerald-500 text-white hover:brightness-95">Edit Filters</button>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <input className="border rounded-full px-3 py-1 text-sm dark:bg-neutral-900 dark:border-neutral-700" placeholder="Search jobs…" value={query} onChange={(e) => setQuery(e.target.value)} />
        </div>
      </div>

      {/* Responsive grid */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Sidebar (hide on small) */}
        <div className="hidden md:block md:col-span-3">
          <div className="rounded-2xl border p-3 bg-white dark:bg-neutral-900 dark:border-neutral-800 sticky top-4">
            <div className="text-xl font-bold flex items-center gap-2 mb-4">
              <span className="text-emerald-500">●</span> Jobright
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex items-center justify-between"><span>Recommended</span><span className="text-neutral-500">{DEMO_JOBS.length}</span></div>
              <div className="flex items-center justify-between"><span>Liked</span><span className="text-neutral-500">{liked.size}</span></div>
              <div className="flex items-center justify-between"><span>Applied</span><span className="text-neutral-500">{applied.size}</span></div>
              <div className="flex items-center justify-between"><span>Saved</span><span className="text-neutral-500">{saved.size}</span></div>
            </div>
          </div>
        </div>

        {/* Feed */}
        <div className="md:col-span-6 space-y-4">
          {filtered.filter(tabFilter).map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onDetails={() => setDrawerJob(job)}
              onLike={() => toggleLike(job.id)}
              onSave={() => toggleSave(job.id)}
              onApply={() => toggleApply(job.id)}
              onAutofill={() => onAutofill(job)}
              liked={isLiked(job.id)}
              saved={isSaved(job.id)}
              applied={isApplied(job.id)}
            />
          ))}
        </div>

        {/* Copilot (sticky on desktop, moves below on mobile) */}
        <div className="md:col-span-3">
          <RightCopilot me={me} selectedJob={drawerJob} token={token} resumes={resumes} />
        </div>
      </div>

      <JobDetailsDrawer
        job={drawerJob}
        open={!!drawerJob}
        onClose={() => setDrawerJob(null)}
        onLike={() => { if (drawerJob) toggleLike(drawerJob.id); }}
        onSave={() => { if (drawerJob) toggleSave(drawerJob.id); }}
        onApply={() => { if (drawerJob) toggleApply(drawerJob.id); }}
        liked={drawerJob ? isLiked(drawerJob.id) : false}
        saved={drawerJob ? isSaved(drawerJob.id) : false}
        applied={drawerJob ? isApplied(drawerJob.id) : false}
        onAutofill={(j) => onAutofill(j)}
      />
    </div>
  );
}

/* ── SHELL / NAV ───────────────────────────────────────────────────── */
function Shell({ me, token, onLogout }) {
  const [tab, setTab] = useState("jobs");
  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900 dark:bg-neutral-950 dark:text-neutral-100">
      <div className="border-b bg-white/60 backdrop-blur dark:bg-neutral-900/60 dark:border-neutral-800">
        <div className="container flex items-center justify-between py-3">
          <div className="flex items-center gap-3">
            <div className="text-2xl font-bold text-emerald-500">●</div>
            <div className="font-semibold">Wazfini Jobright Suite</div>
            <nav className="ml-2 sm:ml-6 hidden md:flex items-center gap-2">
              {["jobs", "resume", "profile", "settings"].map((k) => (
                <button
                  key={k}
                  onClick={() => setTab(k)}
                  className={`px-3 py-1 rounded-lg text-sm ${
                    tab === k ? "bg-neutral-200 dark:bg-neutral-800" : "hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  }`}
                >
                  {k[0].toUpperCase() + k.slice(1)}
                </button>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-neutral-500 hidden sm:block">Signed in as {me.email}</span>
            <button onClick={onLogout} className="rounded-xl px-3 py-2 border text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800">Logout</button>
          </div>
        </div>
      </div>
      {tab === "jobs" && <JobsPage me={me} token={token} />}
      {tab === "resume" && <ResumePage me={me} token={token} onLogout={onLogout} />}
      {tab === "profile" && (
        <div className="container py-10">
          <h1 className="text-xl font-semibold mb-2">Profile</h1>
          <p className="text-sm text-neutral-500 mb-4">Upload your resume to auto-extract contact info and skills.</p>
          <label className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-black text-white cursor-pointer">
            Upload Resume
            <input type="file" accept=".pdf,.doc,.docx,.txt" className="hidden" onChange={async (e) => {
              const f = e.target.files?.[0]; if (!f) return;
              try {
                const form = new FormData(); form.append("file", f);
                const res = await fetch(`${API_BASE}/upload/resume`, { method: "POST", headers: { Authorization: `Bearer ${token}` }, body: form });
                const data = await res.json();
                window.__parsedProfile = data?.parsed || data; // simple demo store
                document.querySelector('#parsedProfileOut').textContent = JSON.stringify(window.__parsedProfile, null, 2);
              } catch (err) { alert("Upload failed"); }
            }} />
          </label>
          <div className="mt-6 p-4 rounded-2xl bg-white shadow">
            <h2 className="font-semibold mb-2">Parsed from Resume</h2>
            <pre id="parsedProfileOut" className="text-xs bg-gray-50 p-3 rounded overflow-x-auto">{window.__parsedProfile ? JSON.stringify(window.__parsedProfile, null, 2) : "—"}</pre>
          </div>
        </div>
      )}
      {tab === "settings" && (
        <div className="container py-10">
          <h1 className="text-xl font-semibold mb-2">Settings</h1>
          <p className="text-sm text-neutral-500">Theme, privacy, and preferences coming soon.</p>
        </div>
      )}
    </div>
  );
}

/* ── ROOT ─────────────────────────────────────────────────────────── */
export default function App() {
  const { token, me, login, register, logout } = useAuth();
  if (!token || !me) {
    return (
      <div className="min-h-screen bg-neutral-50 text-neutral-900 dark:bg-neutral-950 dark:text-neutral-100">
        <div className="container">
          <div className="flex justify-end py-4"><DarkToggle /></div>
          <AuthPanel onLogin={login} onRegister={register} />
        </div>
      </div>
    );
  }
  return <Shell me={me} token={token} onLogout={logout} />;
}
