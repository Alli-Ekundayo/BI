import { FormEvent, useState } from "react";
import { useDatasourceStore } from "../../store/datasourceStore";
import type { DatasourceType } from "../../types";

export function DatasourceModal() {
  const { isDatasourceModalOpen, closeDatasourceModal, setActiveDatasource } =
    useDatasourceStore();
  const [type, setType] = useState<DatasourceType>("postgres");
  const [datasourceId, setDatasourceId] = useState("");

  if (!isDatasourceModalOpen) {
    return null;
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!datasourceId.trim()) {
      return;
    }
    setActiveDatasource({ type, datasource_id: datasourceId.trim() });
    closeDatasourceModal();
    setDatasourceId("");
  }

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" onClick={closeDatasourceModal}>
      <form className="modal-content animate-scale" onSubmit={onSubmit} onClick={(e) => e.stopPropagation()}>
        <h2>Connect Data Source</h2>

        <div className="modal-form-grid">
          <div className="modal-field">
            <label htmlFor="datasource-type" className="modal-label">
              Engine Type
            </label>
            <select
              id="datasource-type"
              value={type}
              onChange={(e) => setType(e.target.value as DatasourceType)}
            >
              <option value="postgres">PostgreSQL</option>
              <option value="mysql">MySQL</option>
              <option value="mongodb">MongoDB</option>
            </select>
          </div>

          <div className="modal-field">
            <label htmlFor="datasource-id" className="modal-label">
              Connection Identifier
            </label>
            <input
              id="datasource-id"
              type="text"
              placeholder="e.g. analytics_warehouse"
              value={datasourceId}
              onChange={(e) => setDatasourceId(e.target.value)}
              autoFocus
            />
          </div>
        </div>

        <div className="modal-actions">
          <button type="button" className="ghost" onClick={closeDatasourceModal}>
            Cancel
          </button>
          <button className="primary" type="submit" disabled={!datasourceId.trim()}>
            Connect
          </button>
        </div>
      </form>
    </div>
  );
}
