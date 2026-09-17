import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { getOverview } from "../api";
import { ErrorIcon } from "./StatusIcons";

/**
 * Default landing view after indexing. Files/chunks/languages come
 * straight from disk + ChromaDB (fast); the description is a short
 * Groq-generated summary — see backend/app/services/overview.py.
 */
export default function Overview({ repoId, repoName }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadOverview() {
    setLoading(true);
    setError("");
    try {
      const result = await getOverview(repoId);
      setData(result);
    } catch (err) {
      setError(err.message || "Failed to load overview.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadOverview();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repoId]);

  return (
    <section className="card">
      <h2>Overview</h2>
      <p className="muted">{repoName}</p>

      {loading && (
        <div className="loading-note">
          <span className="spinner" />
          Gathering stats and summarizing the project…
        </div>
      )}

      {error && (
        <div className="status-box error">
          <ErrorIcon />
          <span>{error}</span>
        </div>
      )}

      {data && (
        <>
          <div className="stat-grid">
            <div className="stat-tile">
              <span className="stat-value">{data.files_scanned}</span>
              <span className="stat-label">Files</span>
            </div>
            <div className="stat-tile">
              <span className="stat-value">{data.chunks_found}</span>
              <span className="stat-label">Chunks</span>
            </div>
            <div className="stat-tile">
              <span className="stat-value stat-value-text">
                {data.languages.length > 0 ? data.languages.join(", ") : "—"}
              </span>
              <span className="stat-label">Languages</span>
            </div>
          </div>

          <div className="info-card">
            <div className="info-card-title">Project Info</div>
            <div className="markdown">
              <ReactMarkdown>{data.description}</ReactMarkdown>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
