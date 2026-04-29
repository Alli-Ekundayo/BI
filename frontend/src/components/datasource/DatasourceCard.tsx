import { useDatasourceStore } from "../../store/datasourceStore";

export function DatasourceCard() {
  const { activeDatasource, openDatasourceModal, setActiveDatasource } =
    useDatasourceStore();

  if (!activeDatasource) {
    return (
      <section className="card datasource-card-empty">
        <h3>No active connection</h3>
        <p className="subtle-text">Connect a data source to begin querying.</p>
        <button className="primary datasource-cta" onClick={openDatasourceModal}>
          Connect Data Source
        </button>
      </section>
    );
  }

  return (
    <section className="card">
      <div>
        <p className="kicker">Connected</p>
        <h3 className="datasource-name">{activeDatasource.datasource_id}</h3>
        <p className="datasource-type">{activeDatasource.type}</p>
      </div>
      <div className="datasource-actions">
        <button className="ghost" onClick={openDatasourceModal}>
          Switch
        </button>
        <button className="ghost disconnect-btn" onClick={() => setActiveDatasource(null)}>
          Disconnect
        </button>
      </div>
    </section>
  );
}
