import React, { useState } from "react";
import { api, setToken } from "../lib/api.js";

export default function LoginPage() {
  const [email, setEmail] = useState("adam2@example.com");
  const [password, setPassword] = useState("123456");
  const [msg, setMsg] = useState("");

  async function handle(e) {
    e.preventDefault();
    try {
      const data = await api.login(email, password);
      setToken(data.access_token);
      setMsg("Logged in!");
    } catch (err) {
      setMsg("Login failed");
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>Login</h2>
      <form onSubmit={handle}>
        <input value={email} onChange={(e) => setEmail(e.target.value)} />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ marginLeft: 8 }}
        />
        <button style={{ marginLeft: 8 }}>Login</button>
      </form>
      <div>{msg}</div>
    </div>
  );
}
