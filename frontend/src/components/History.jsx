import { useEffect, useState } from "react";
import { getHistory } from "../api";
import { formatUtcTimestamp } from "../utils";

/**
 * Step 3 of the UI: past Q&A pairs for the current repo, most recent
 * first (the backend's SQL query already orders them — this component
 * just renders what GET /repos/{repo_id}/history returns).
 *
 * Note: history rows only store question + answer text (see
 * backend/app/database.py's ChatHistory model), not source references,
 * so past entries here don't show file/line citations — ask again in
 * the Chat tab to see those.
 */
export default function History({ repoId, repoName }) {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadHistory() {
    setLoading(true);
    setError("");
    try {
      const data = await getHistory(repoId);
      setEntries(data.history);
    } catch (err) {
      setError(err.message || "Failed to load history.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repoId]);

  return (
    <section className="card">
      <div className="history-header">
        <div>
          <h2>History for {repoName}</h2>
          <p className="muted">Past questions and answers, most recent first.</p>
        </div>
        <button className="btn btn-secondary" onClick={loadHistory} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {error && <div className="error-box">{error}</div>}

      {!loading && !error && entries.length === 0 && (
        <p className="muted">No questions asked yet — try the Chat tab.</p>
      )}

      <ul className="history-list">
        {entries.map((entry) => (
          <li key={entry.id} className="history-item">
            <div className="history-time">
              {formatUtcTimestamp(entry.created_at)}
            </div>
            <div className="history-question">Q: {entry.question}</div>
            <div className="history-answer">A: {entry.answer}</div>
          </li>
        ))}
      </ul>
    </section>
  );
}
