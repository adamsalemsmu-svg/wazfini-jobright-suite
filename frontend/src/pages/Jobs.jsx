import React, { useEffect, useState } from "react";
import { api } from "../lib/api.js";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [location, setLocation] = useState("Dubai");

  useEffect(() => {
    (async () => {
      try {
        const data = await api.jobs();
        setJobs(data);
      } catch (e) {
        console.error(e);
      }
    })();
  }, []);

  async function search() {
    try {
      const data = await api.search({ location });
      setJobs(data);
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>Jobs</h2>
      <input value={location} onChange={(e) => setLocation(e.target.value)} />
      <button onClick={search} style={{ marginLeft: 8 }}>Search</button>
      <ul>
        {jobs.map((j) => (
          <li key={j.id}>
            <b>{j.title}</b> — {j.company} ({j.location})
          </li>
        ))}
      </ul>
    </div>
  );
}
