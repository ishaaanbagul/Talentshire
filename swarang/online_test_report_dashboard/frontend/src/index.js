
import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import TestCases from "./TestCases.jsx";

const Router = () => {
  const [view, setView] = useState("app"); // "app" or "testcases"

  return (
    <div>
      {view === "app" ? (
        <>
          <div style={{
            position: "fixed",
            top: "12px",
            right: "12px",
            zIndex: 9999,
            display: "flex",
            gap: "8px"
          }}>
            <button 
              onClick={() => setView("testcases")}
              style={{
                padding: "8px 16px",
                background: "#1e3a5f",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "12px",
                fontWeight: "600"
              }}
            >
              View Test Cases
            </button>
          </div>
          <App />
        </>
      ) : (
        <>
          <div style={{
            position: "fixed",
            top: "12px",
            right: "12px",
            zIndex: 9999,
            display: "flex",
            gap: "8px"
          }}>
            <button 
              onClick={() => setView("app")}
              style={{
                padding: "8px 16px",
                background: "#1e3a5f",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "12px",
                fontWeight: "600"
              }}
            >
              Back to Main Report
            </button>
          </div>
          <TestCases />
        </>
      )}
    </div>
  );
};

const root = createRoot(document.getElementById("root"));
root.render(<Router />);
