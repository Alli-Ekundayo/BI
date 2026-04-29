import { AppShell } from "./components/layout/AppShell";
import { DatasourceModal } from "./components/datasource/DatasourceModal";
import { QueryBar } from "./components/query/QueryBar";
import { ResultsPanel } from "./components/results/ResultsPanel";

export default function App() {
  return (
    <>
      <AppShell>
        <section className="hero animate-in">
          <h2>Intelligence on Demand</h2>
          <p>
            Query your business data using natural language. Get instant SQL,
            interactive charts, and deep insights.
          </p>
        </section>

        <div className="animate-in">
          <QueryBar />
        </div>

        <div className="animate-in">
          <ResultsPanel />
        </div>
      </AppShell>
      <DatasourceModal />
    </>
  );
}
