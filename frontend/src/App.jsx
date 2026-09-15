import { useState } from "react";
import RepoInput from "./components/RepoInput";
import Chat from "./components/Chat";
import History from "./components/History";
import Logo from "./components/Logo";

/**
 * Top-level layout: a tab bar over one of three views. `repo` holds the
 * currently indexed repo (set once RepoInput's POST /repos/index call
 * succeeds); Chat and History are disabled until it's set, and are both
 * keyed by repo.repoId so switching to a newly indexed repo resets their
 * internal state instead of showing the previous repo's messages/history.
 */
export default function App() {
  const [repo, setRepo] = useState(null);
  const [activeTab, setActiveTab] = useState("index");

  function handleIndexed(repoInfo) {
    setRepo(repoInfo);
    setActiveTab("chat");
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <Logo />
          <div className="brand-text">
            <span className="brand-name">Codebase Onboarding Agent</span>
            {repo && <span className="brand-context">{repo.repoName}</span>}
          </div>
        </div>

        <nav className="tab-nav">
          <button
            className={"tab-button" + (activeTab === "index" ? " active" : "")}
            onClick={() => setActiveTab("index")}
          >
            Index Repo
          </button>
          <button
            className={"tab-button" + (activeTab === "chat" ? " active" : "")}
            onClick={() => setActiveTab("chat")}
            disabled={!repo}
          >
            Chat
          </button>
          <button
            className={"tab-button" + (activeTab === "history" ? " active" : "")}
            onClick={() => setActiveTab("history")}
            disabled={!repo}
          >
            History
          </button>
        </nav>
      </header>

      {activeTab === "index" && <RepoInput onIndexed={handleIndexed} />}

      {activeTab === "chat" && repo && (
        <Chat key={repo.repoId} repoId={repo.repoId} repoName={repo.repoName} />
      )}

      {activeTab === "history" && repo && (
        <History key={repo.repoId} repoId={repo.repoId} repoName={repo.repoName} />
      )}
    </div>
  );
}
