/**
 * Placeholder for the Overview tab — sidebar layout ships first (this
 * component just proves the nav wiring works); the real stat tiles +
 * LLM project summary come from a dedicated backend endpoint next.
 */
export default function Overview({ repoName }) {
  return (
    <section className="card">
      <h2>Overview</h2>
      <p className="muted">{repoName}</p>
      <p style={{ marginTop: 16 }}>
        Project stats and an AI-generated summary will appear here next.
      </p>
    </section>
  );
}
