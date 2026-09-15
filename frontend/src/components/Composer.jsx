import React, { useState } from "react";

const MODES = [
  { id: null, label: "Ask" },
  { id: "ship30", label: "Ship 30 essay" },
  { id: "artifact", label: "Artifact" },
];

export function Composer({ onSend, disabled, value, onChange }) {
  const [mode, setMode] = useState(null);

  function submit() {
    if (!value.trim() || disabled) return;
    onSend(value, mode);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="composer">
      <div className="mode-pills">
        {MODES.map((m) => (
          <button
            key={m.label}
            className={`mode-pill ${mode === m.id ? "active" : ""}`}
            onClick={() => setMode(m.id)}
            type="button"
          >
            {m.label}
          </button>
        ))}
      </div>
      <div className="composer-row">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a product or growth question…"
        />
        <button className="send-btn" onClick={submit} disabled={disabled}>
          Send
        </button>
      </div>
    </div>
  );
}
