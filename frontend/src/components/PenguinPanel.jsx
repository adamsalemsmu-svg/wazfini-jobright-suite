import React, { useState } from "react";
import { api } from "../lib/api.js";

export default function PenguinPanel() {
  const [jobId, setJobId] = useState(1);
  const [question, setQuestion] = useState(
    "How should I tailor my resume for this role in Dubai?"
  );
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);

  async function ask() {
    setLoading(true);
    setReply("");
    try {
      const res = await api.chat({ job_id: jobId, question, use_active_resume: true });
      setReply(res.answer);
    } catch (e) {
      setReply("Error: " + (e?.message || String(e)));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <h3>🐧 Penguin (AI Assistant)</h3>
      <div style={{ marginBottom: 8 }}>
        <label>Job ID:&nbsp;</label>
        <input
          type="number"
          value={jobId}
          onChange={(e) => setJobId(parseInt(e.target.value || "1", 10))}
          style={{ width: 80 }}
        />
      </div>
      <textarea
        rows={4}
        style={{ width: "100%" }}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button onClick={ask} disabled={loading} style={{ marginTop: 8 }}>
        {loading ? "Asking..." : "Ask Penguin"}
      </button>
      <pre style={{ whiteSpace: "pre-wrap", marginTop: 12 }}>{reply}</pre>
    </div>
  );
}
