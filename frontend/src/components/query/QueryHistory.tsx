import { useQueryStore } from "../../store/queryStore";

export function QueryHistory() {
  const { history, selectResult, latestResult, clearResults } = useQueryStore();

  const extractFirstHeader = (text: string) => {
    // Look for lines starting with # (markdown headers)
    const headerMatch = text.match(/^#+\s+(.*)$/m);
    if (headerMatch) {
      return headerMatch[1].trim();
    }
    // Fallback: truncate first line or use first 40 chars
    const firstLine = text.split('\n')[0].trim();
    return firstLine.length > 40 ? firstLine.slice(0, 37) + "..." : firstLine;
  };

  if (history.length === 0) {
    return (
      <div className="empty-state empty-state--compact">
        <p>No recent queries.</p>
        <p className="subtle-text">Your query history will appear here.</p>
      </div>
    );
  }

  return (
    <div className="history-container">
      <ul className="history-list">
        {history.slice(0, 10).map((item, idx) => (
          <li 
            key={`${item.session_id}-${idx}`} 
            className={`history-item ${latestResult?.query_generated === item.query_generated ? 'active' : ''}`}
            onClick={() => selectResult(item)}
            role="button"
            tabIndex={0}
          >
            <p className="history-answer">
              {extractFirstHeader(item.answer || "No summary available")}
            </p>
            <p className="history-query">
              {item.query_generated?.slice(0, 50)}
              {item.query_generated && item.query_generated.length > 50 ? "..." : ""}
            </p>
          </li>
        ))}
      </ul>
      <div style={{ marginTop: 'var(--space-md)' }}>
        <button className="ghost" style={{ width: '100%', fontSize: '0.75rem', minHeight: '32px' }} onClick={clearResults}>
          Clear History
        </button>
      </div>
    </div>
  );
}
