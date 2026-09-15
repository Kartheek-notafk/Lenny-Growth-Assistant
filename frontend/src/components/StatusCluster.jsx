import React from "react";

/** Small mixing-desk-style status readout — provider + DB reachability,
 * not a decorative badge. Values come straight from GET /health. */
export function StatusCluster({ health }) {
  const dbClass = !health ? "unknown" : health.database === "up" ? "" : "down";
  const dbLabel = !health ? "checking" : health.database;
  return (
    <div className="status-cluster">
      <div className="status-item">
        <span className={`status-dot ${dbClass}`} />
        <span>db · {dbLabel}</span>
      </div>
      <div className="status-item">
        <span className="status-dot" />
        <span>model · {health ? health.provider : "…"}</span>
      </div>
    </div>
  );
}
