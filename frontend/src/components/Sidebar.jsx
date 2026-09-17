import Logo from "./Logo";
import {
  OverviewIcon,
  ChatIcon,
  HistoryIcon,
  SettingsIcon,
  OnboardingIcon,
  EvaluationIcon,
} from "./NavIcons";

const NAV_ITEMS = [
  { id: "overview", label: "Overview", Icon: OverviewIcon, requiresRepo: true },
  { id: "chat", label: "Ask AI", Icon: ChatIcon, requiresRepo: true },
  { id: "history", label: "History", Icon: HistoryIcon, requiresRepo: true },
  { id: "onboarding", label: "Onboarding", Icon: OnboardingIcon, requiresRepo: true },
  { id: "evaluation", label: "Evaluation", Icon: EvaluationIcon, requiresRepo: true },
  { id: "settings", label: "Settings", Icon: SettingsIcon, requiresRepo: false },
];

export default function Sidebar({ activeTab, onSelectTab, repo }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <Logo size={24} />
        <span className="sidebar-brand-name">Codebase Agent</span>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ id, label, Icon, requiresRepo }) => (
          <button
            key={id}
            className={"sidebar-nav-item" + (activeTab === id ? " active" : "")}
            onClick={() => onSelectTab(id)}
            disabled={requiresRepo && !repo}
          >
            <Icon />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        {repo ? (
          <>
            <div className="sidebar-footer-label">Current repo</div>
            <div className="sidebar-footer-repo" title={repo.repoName}>
              {repo.repoName}
            </div>
          </>
        ) : (
          <div className="sidebar-footer-label">No repo indexed</div>
        )}
      </div>
    </aside>
  );
}
