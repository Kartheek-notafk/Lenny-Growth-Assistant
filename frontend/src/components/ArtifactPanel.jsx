import React, { useMemo } from "react";

/** Wraps the raw artifact string in a minimal styled HTML shell for the
 * sandboxed iframe. If the content already looks like HTML it renders as-is;
 * otherwise (Markdown) it's shown as readable preformatted text — a
 * deliberate simplification over full Markdown rendering, documented in
 * docs/architecture.md, since the security story (sandboxed, scriptless
 * iframe) matters more than typographic fidelity for this submission. */
function buildDoc(raw) {
  const looksLikeHtml = raw.trim().startsWith("<");
  const body = looksLikeHtml
    ? raw
    : `<pre style="white-space:pre-wrap;font-family:inherit;margin:0">${raw
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")}</pre>`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    body{font-family:'IBM Plex Sans',sans-serif;color:#20242B;background:#FAF6EA;
         padding:22px;line-height:1.6;font-size:14px}
    h1,h2,h3{font-family:'Fraunces',serif;font-weight:500}
    a{color:#AE5236}
  </style></head><body>${body}</body></html>`;
}

export function ArtifactPanel({ artifact }) {
  const doc = useMemo(() => (artifact ? buildDoc(artifact) : null), [artifact]);

  return (
    <div className="artifact-surface">
      <div className="artifact-card">
        {doc ? (
          <iframe title="artifact" sandbox="" srcDoc={doc} />
        ) : (
          <div className="artifact-empty">
            <p>
              Ask for a Ship 30 essay or an artifact and the rendered
              Markdown or HTML shows up here, beside the conversation.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
