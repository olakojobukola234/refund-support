import { useEffect, useState } from "react";
import { fetchRequests } from "../api";

const AI_STATUS_LABELS = {
  local: "Local rules",
  not_used: "Not used",
  success: "AI used",
  quota_exceeded: "Quota exceeded",
  unavailable: "Provider unavailable",
  not_configured: "Not configured",
  error: "Provider error",
};
const AI_FAILURE_STATUSES = new Set(["quota_exceeded", "unavailable", "not_configured", "error"]);

export default function Dashboard() {
  const [rows, setRows] = useState([]);
  const [filter, setFilter] = useState("All");
  const [error, setError] = useState("");

  async function load() {
    try {
      setRows(await fetchRequests());
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    const initialLoad = setTimeout(load, 0);
    const t = setInterval(load, 10000);
    return () => {
      clearTimeout(initialLoad);
      clearInterval(t);
    };
  }, []);

  const shown = filter === "All" ? rows : rows.filter((r) => r.decision === filter);
  const count = (d) => rows.filter((r) => r.decision === d).length;
  const aiIssues = rows.filter((r) => AI_FAILURE_STATUSES.has(r.ai_status));

  return (
    <div className="card wide">
      <div className="row">
        <h2>Support dashboard</h2>
        <button onClick={load}>Refresh</button>
      </div>
      <div className="stats">
        <span className="badge Approved">Approved {count("Approved")}</span>
        <span className="badge Denied">Denied {count("Denied")}</span>
        <span className="badge Escalated">Escalated {count("Escalated")}</span>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          {["All", "Approved", "Denied", "Escalated"].map((o) => <option key={o}>{o}</option>)}
        </select>
      </div>
      {aiIssues.length > 0 && (
        <div className="ai-warning" role="status">
          AI assistance failed for {aiIssues.length} recent request{aiIssues.length === 1 ? "" : "s"}.
          Check the AI status and audit note below. Policy-only decisions remain available.
        </div>
      )}
      {error && <p className="error">{error}</p>}
      <div className="scroll">
        <table>
          <thead>
            <tr><th>Time</th><th>Customer</th><th>Order</th><th>Decision</th><th>Rule</th><th>AI status</th><th>Audit notes</th></tr>
          </thead>
          <tbody>
            {shown.map((r) => (
              <tr key={r.id}>
                <td>{new Date(r.created_at).toLocaleString()}</td>
                <td>{r.customer_email}</td>
                <td>{r.order_id || "-"}</td>
                <td><span className={`badge ${r.decision}`}>{r.decision}</span></td>
                <td><code>{r.rule}</code></td>
                <td><span className={`ai-status ${r.ai_status}`}>{AI_STATUS_LABELS[r.ai_status] || "Unknown"}</span></td>
                <td>
                  <div><b>Message:</b> {r.message}</div>
                  <div><b>Reason detected:</b> {r.reason}</div>
                  <div><b>Policy:</b> {r.reasons.join(" ")}</div>
                  <div><b>AI summary:</b> {r.ai_notes}</div>
                  {r.injection_flag && <div className="error">Possible prompt injection</div>}
                </td>
              </tr>
            ))}
            {shown.length === 0 && <tr><td colSpan="7" className="muted">No requests yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}