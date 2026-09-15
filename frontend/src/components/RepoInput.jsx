import { useState } from "react";
import { indexRepo } from "../api";

/**
 * Step 1 of the UI: paste a GitHub URL, trigger POST /repos/index,
 * and show progress → success (or error). On success, the parent App
 * gets the indexed repo's info via onIndexed() and switches to Chat.
 */
export default function RepoInput({ onIndexed }) {
  const [repoUrl, setRepoUrl] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmed = repoUrl.trim();
    if (!trimmed) return;

    setStatus("loading");
    setErrorMessage("");
    try {
      const data = await indexRepo(trimmed);
      setResult(data);
      setStatus("success");
    } catch (err) {
      setErrorMessage(err.message || "Failed to index repository.");
      setStatus("error");
    }
  }

  return (
    <section className="card">
      <h2>Index a GitHub Repository</h2>
      <p className="muted">
        Paste a public GitHub repo URL. The backend clones it, parses
        Python/JS files into chunks, embeds them, and stores the vectors in
        ChromaDB.
      </p>

      <form onSubmit={handleSubmit} className="field-row">
        <input
          type="text"
          className="text-input"
          placeholder="https://github.com/owner/repo"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          disabled={status === "loading"}
        />
        <button
          type="submit"
          className="btn"
          disabled={status === "loading" || !repoUrl.trim()}
        >
          {status === "loading" ? "Indexing…" : "Index Repository"}
        </button>
      </form>

      {status === "loading" && (
        <div className="loading-note">
          <span className="spinner" />
          Cloning the repo, parsing source files, and generating
          embeddings — this can take a while for larger repositories.
        </div>
      )}

      {status === "error" && <div className="error-box">{errorMessage}</div>}

      {status === "success" && result && (
        <div className="success-panel">
          <p>
            ✅ Indexed <strong>{result.repo_name}</strong> successfully.
          </p>
          <div className="stat-grid">
            <div className="stat-tile">
              <span className="stat-value">{result.files_scanned}</span>
              <span className="stat-label">Files scanned</span>
            </div>
            <div className="stat-tile">
              <span className="stat-value">{result.chunks_found}</span>
              <span className="stat-label">Chunks found</span>
            </div>
            <div className="stat-tile">
              <span className="stat-value">{result.chunks_embedded}</span>
              <span className="stat-label">Chunks embedded</span>
            </div>
          </div>
          <button
            className="btn"
            onClick={() =>
              onIndexed({
                repoId: result.repo_id,
                repoName: result.repo_name,
              })
            }
          >
            Start Chatting →
          </button>
        </div>
      )}
    </section>
  );
}
