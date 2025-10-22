import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import JobsPage from "./pages/Jobs.jsx";
import LoginPage from "./pages/Login.jsx";
import PenguinPanel from "./components/PenguinPanel.jsx";

function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: 12, borderBottom: "1px solid #ddd" }}>
        <Link to="/">Jobs</Link> | <Link to="/penguin">Penguin</Link> |{" "}
        <Link to="/login">Login</Link>
      </nav>
      <Routes>
        <Route path="/" element={<JobsPage />} />
        <Route path="/penguin" element={<PenguinPanel />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
