import { useSchema } from "../../hooks/useSchema";
import { SchemaTree } from "./SchemaTree";

export function SchemaPanel() {
  const { schema, isLoading, error } = useSchema();

  if (isLoading) {
    return <p className="loading-state">Analyzing tables...</p>;
  }

  if (error) {
    return <p className="error-state">{error}</p>;
  }

  if (!schema || Object.keys(schema.tables).length === 0) {
    return (
      <div className="empty-state">
        <p>No schema metadata found.</p>
        <p className="subtle-text">Connect a data source to view table information.</p>
      </div>
    );
  }

  return (
    <div className="schema-panel-scroll">
      <SchemaTree tables={schema.tables} />
    </div>
  );
}
