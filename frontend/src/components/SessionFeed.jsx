import React, { useEffect, useRef } from "react";

const STARTER_PROMPTS = [
  "How do I know if I've found product-market fit?",
  "What's a good way to run a pricing experiment?",
  "How should an early PM think about growth loops?",
];

function Citations({ sources }) {
  if (!sources || sources.length === 0) return null;
  return (
    <div className="citations">
      {sources.slice(0, 4).map((s, i) => (
        <div className="citation-chip" key={i}>
          <span className="guest">{s.guest || s.title}</span>
          <span className="file">{s.source}</span>
        </div>
      ))}
    </div>
  );
}

export function SessionFeed({ turns, pending, onPrompt }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [turns, pending]);

  if (turns.length === 0 && !pending) {
    return (
      <div className="session-surface" ref={scrollRef}>
        <div className="empty-state">
          <h3>Nothing on the tape yet</h3>
          <p>
            Ask a product or growth question and the assistant will answer
            from Lenny's Podcast transcripts, citing exactly which episode it
            drew from.
          </p>
          <div className="prompts">
            {STARTER_PROMPTS.map((p) => (
              <button key={p} onClick={() => onPrompt(p)}>
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="session-surface" ref={scrollRef}>
      {turns.map((t, i) => (
        <div className={`turn ${t.role}`} key={i}>
          <div className="turn-head">
            <span className="speaker">{t.role === "user" ? "You" : "Assistant"}</span>
            {t.skill && <span className="speaker">· {t.skill}</span>}
          </div>
          <div className={`turn-body ${t.error ? "error" : ""}`}>{t.content}</div>
          {t.grounded === false && t.role === "assistant" && (
            <div className="grounding-note">not grounded in the transcript archive</div>
          )}
          <Citations sources={t.sources} />
        </div>
      ))}
      {pending && (
        <div className="turn assistant">
          <div className="turn-head">
            <span className="speaker">Assistant</span>
          </div>
          <div className="turn-body pending">
            listening to the archive
            <span className="rec-tick" />
          </div>
        </div>
      )}
    </div>
  );
}
