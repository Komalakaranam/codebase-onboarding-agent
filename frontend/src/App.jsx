import { useState } from "react";
import Sidebar from "./components/Sidebar";
import RepoInput from "./components/RepoInput";
import Overview from "./components/Overview";
import Chat from "./components/Chat";
import History from "./components/History";
import Onboarding from "./components/Onboarding";

/**
 * Layout: a fixed sidebar (nav + branding) beside a scrollable main
 * content area. `repo` holds the currently indexed repo; Overview/Chat/
 * History are disabled in the sidebar until it's set. Settings always
 * holds the repo-indexing form, so switching repos is just "go to
 * Settings and index a new URL" rather than a separate first-run screen.
 */
export default function App() {
  const [repo, setRepo] = useState(null);
  const [activeTab, setActiveTab] = useState("settings");

  function handleIndexed(repoInfo) {
    setRepo(repoInfo);
    setActiveTab("overview");
  }

  return (
    <div className="app-layout">
      <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} repo={repo} />

      <main className="main-content">
        <div className="content-inner">
          {activeTab === "settings" && <RepoInput onIndexed={handleIndexed} />}

          {activeTab === "overview" && repo && (
            <Overview key={repo.repoId} repoId={repo.repoId} repoName={repo.repoName} />
          )}

          {activeTab === "chat" && repo && (
            <Chat key={repo.repoId} repoId={repo.repoId} repoName={repo.repoName} />
          )}

          {activeTab === "history" && repo && (
            <History key={repo.repoId} repoId={repo.repoId} repoName={repo.repoName} />
          )}

          {activeTab === "onboarding" && repo && (
            <Onboarding key={repo.repoId} repoId={repo.repoId} repoName={repo.repoName} />
          )}
        </div>
      </main>
    </div>
  );
}
