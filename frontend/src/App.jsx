import React, { useEffect, useState, useCallback } from "react";
import { api } from "./api";
import { StatusCluster } from "./components/StatusCluster";
import { SessionFeed } from "./components/SessionFeed";
import { Composer } from "./components/Composer";
import { ArtifactPanel } from "./components/ArtifactPanel";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [turns, setTurns] = useState([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [artifact, setArtifact] = useState(null);
  const [health, setHealth] = useState(null);

  const startSession = useCallback(async () => {
    setTurns([]);
    setArtifact(null);
    try {
      const { session_id } = await api.newSession();
      setSessionId(session_id);
    } catch {
      // No backend yet — fall back to a client-side id so the UI still works;
      // messages just won't persist server-side until the API is reachable.
      setSessionId(crypto.randomUUID());
    }
  }, []);

  useEffect(() => {
    startSession();
    api.health().then(setHealth).catch(() => setHealth({ provider: "unknown", database: "down" }));
  }, [startSession]);

  async function handleSend(message, skill) {
    setTurns((t) => [...t, { role: "user", content: message, skill }]);
    setInput("");
    setPending(true);
    try {
      const data = await api.chat(sessionId, message, skill);
      setTurns((t) => [
        ...t,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          grounded: data.grounded,
          skill,
        },
      ]);
      if (data.artifact) setArtifact(data.artifact);
    } catch (e) {
      setTurns((t) => [
        ...t,
        { role: "assistant", content: `Couldn't reach the assistant: ${e.message}`, error: true },
      ]);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark live" />
          <h1>The Lenny Growth Assistant</h1>
          <span className="tag">session {sessionId ? sessionId.slice(0, 8) : "…"}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <StatusCluster health={health} />
          <button className="new-session-btn" onClick={startSession}>
            New session
          </button>
        </div>
      </header>

      <div className="workspace">
        <section className="pane">
          <div className="pane-header">
            <h2>Session</h2>
            <span className="hint">grounded in Lenny's Podcast transcripts</span>
          </div>
          <SessionFeed turns={turns} pending={pending} onPrompt={(p) => handleSend(p, null)} />
          <Composer onSend={handleSend} disabled={pending || !sessionId} value={input} onChange={setInput} />
        </section>

        <section className="pane">
          <div className="pane-header">
            <h2>Artifact</h2>
            <span className="hint">Markdown / HTML</span>
          </div>
          <ArtifactPanel artifact={artifact} />
          <p className="security-note">
            <b>Rendered in a sandboxed iframe</b> (<code>sandbox=""</code>) with scripts, forms
            and same-origin access all disabled — generated HTML can style
            itself but can't run code or read the parent page.
          </p>
        </section>
      </div>
    </div>
  );
}
