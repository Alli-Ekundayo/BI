import { useDatasourceStore } from "../../store/datasourceStore";
import { useSessionStore } from "../../store/sessionStore";

export function Header() {
  const { openDatasourceModal } = useDatasourceStore();
  const { clearSession } = useSessionStore();

  return (
    <header className="masthead animate-in">
      <div>
        <p className="kicker">BI Bot Engine</p>
        <h1>Control Surface</h1>
        <p>Intelligent data exploration and automated insights.</p>
      </div>
      <div className="action-cluster">
        <button className="ghost" onClick={clearSession}>
          Reset Session
        </button>
        <button className="primary" onClick={openDatasourceModal}>
          Connect Data
        </button>
      </div>
    </header>
  );
}
