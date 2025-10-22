// frontend/src/main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./ui/App.jsx";
import "./ui/index.css"; // ✅ if file is exactly under src/ui


ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
