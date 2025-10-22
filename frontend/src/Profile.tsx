import React, { useState } from "react";
import { uploadResumeFile } from "../lib/api";

export default function Profile() {
  const [parsed, setParsed] = useState<any | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    setErr(null);
    setBusy(true);
    try {
      const res = await uploadResumeFile(f);
      setParsed(res.parsed || res);
    } catch (e: any) {
      setErr(e.message || "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-2">Profile</h1>
      <p className="text-sm text-gray-600 mb-4">
        Upload your resume to auto-extract contact info and skills.
      </p>

      <label className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-black text-white cursor-pointer">
        Upload Resume
        <input type="file" accept=".pdf,.doc,.docx,.txt" className="hidden" onChange={onFile} />
      </label>

      {busy && <div className="mt-3 text-sm">Parsing…</div>}
      {err && <div className="mt-3 text-sm text-red-600">{err}</div>}

      {parsed && (
        <div className="mt-6 grid gap-4">
          <div className="p-4 rounded-2xl bg-white shadow">
            <h2 className="font-semibold mb-2">Personal</h2>
            <div className="text-sm grid gap-1">
              <div>Email: {parsed.email || "—"}</div>
              <div>Phone: {parsed.phone || "—"}</div>
              <div>LinkedIn: {parsed.linkedin || "—"}</div>
              <div>GitHub: {parsed.github || "—"}</div>
            </div>
          </div>
          <div className="p-4 rounded-2xl bg-white shadow">
            <h2 className="font-semibold mb-2">Skills</h2>
            <div className="flex flex-wrap gap-2">
              {(parsed.skills || []).map((s: string) => (
                <span key={s} className="px-3 py-1 rounded-full border bg-gray-50 text-sm">
                  {s}
                </span>
              ))}
              {(!parsed.skills || parsed.skills.length === 0) && <span>—</span>}
            </div>
          </div>
          <div className="p-4 rounded-2xl bg-white shadow">
            <h2 className="font-semibold mb-2">Raw Parse</h2>
            <pre className="text-xs bg-gray-50 p-3 rounded overflow-x-auto">
{JSON.stringify(parsed, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
