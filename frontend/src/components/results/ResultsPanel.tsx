import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useMemo, useState } from "react";
import { useQueryStore } from "../../store/queryStore";
import type { VizType } from "../../types";
import { DataTable } from "./DataTable";
import { ChartView } from "./ChartView";
import { RawJSON } from "./RawJSON";

type ResultTab = "table" | "chart" | "json";

export function ResultsPanel() {
  const { latestResult, error } = useQueryStore();
  const [tab, setTab] = useState<ResultTab>("table");

  const vizType = useMemo<VizType>(() => latestResult?.viz_type ?? "table", [latestResult]);

  if (!latestResult && !error) return null;

  return (
    <section className="results-container animate-in">
      <header className="results-header">
        <div style={{ width: "100%" }}>
          <p className="kicker">Executive Summary</p>
          <div className="card answer-card markdown-content">
            {latestResult?.answer ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {latestResult.answer}
              </ReactMarkdown>
            ) : (
              "Awaiting input..."
            )}
          </div>
        </div>
        <nav className="tabs" aria-label="Result views" role="tablist">
          <button
            type="button"
            className={tab === "table" ? "active" : ""}
            onClick={() => setTab("table")}
            role="tab"
            aria-selected={tab === "table"}
          >
            Data Table
          </button>
          <button
            type="button"
            className={tab === "chart" ? "active" : ""}
            onClick={() => setTab("chart")}
            role="tab"
            aria-selected={tab === "chart"}
          >
            Visualization
          </button>
          <button
            type="button"
            className={tab === "json" ? "active" : ""}
            onClick={() => setTab("json")}
            role="tab"
            aria-selected={tab === "json"}
          >
            Raw JSON
          </button>
        </nav>
      </header>

      {error && (
        <div className="error-state" role="alert">
          <strong>Error:</strong> {error}
        </div>
      )}

      {latestResult && (
        <div className="results-content animate-in">
          <div className="results-sql-block">
            <p className="kicker">Generated Logic</p>
            <pre className="generated-sql">
              {latestResult.query_generated || "-- No logic generated."}
            </pre>
          </div>

          <div className="card results-output-card">
            {tab === "table" && <DataTable rows={latestResult.results} />}
            {tab === "chart" && <ChartView rows={latestResult.results} vizType={vizType} />}
            {tab === "json" && <RawJSON rows={latestResult.results} />}
          </div>
        </div>
      )}
    </section>
  );
}
