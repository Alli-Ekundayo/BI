import { FormEvent, useState } from "react";
import { useQuery } from "../../hooks/useQuery";
import { useQueryStore } from "../../store/queryStore";

export function QueryBar() {
  const [message, setMessage] = useState("");
  const { runQuery } = useQuery();
  const { isLoading } = useQueryStore();

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || isLoading) {
      return;
    }
    await runQuery(trimmed);
    setMessage("");
  }

  return (
    <form className="query-container" onSubmit={onSubmit}>
      <div className="query-box">
        <label htmlFor="query-input" className="kicker">
          Ask a business question
        </label>
        <textarea
          id="query-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="What are the top 5 regions by revenue growth this month?"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              e.currentTarget.form?.requestSubmit();
            }
          }}
        />
        <div className="query-footer">
          <span className="query-submit-hint">Press Enter to analyze</span>
          <button className="primary" type="submit" disabled={isLoading || !message.trim()}>
            {isLoading ? "Analyzing..." : "Execute Insight"}
          </button>
        </div>
      </div>
    </form>
  );
}
