import type { SchemaField } from "../../types";

interface SchemaTreeProps {
  tables: Record<string, SchemaField[]>;
}

export function SchemaTree({ tables }: SchemaTreeProps) {
  const entries = Object.entries(tables);

  if (entries.length === 0) {
    return <p className="schema-empty">Metadata unavailable.</p>;
  }

  return (
    <div className="schema-tree">
      {entries.map(([table, columns]) => (
        <details key={table} className="schema-group">
          <summary className="schema-summary">
            {table}
          </summary>
          <ul className="schema-columns">
            {columns.map((column) => (
              <li key={`${table}-${column.column}`} className="schema-column">
                <span className="schema-column-name">{column.column}</span>
                <em className="schema-column-type">{column.type}</em>
              </li>
            ))}
          </ul>
        </details>
      ))}
    </div>
  );
}
