interface DataTableProps {
  rows: Record<string, unknown>[];
}

export function DataTable({ rows }: DataTableProps) {
  if (rows.length === 0) {
    return (
      <div className="empty-state">
        <p>No data points found.</p>
        <p className="subtle-text">Try adjusting your query or check the data source.</p>
      </div>
    );
  }

  const headers = Object.keys(rows[0]);

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 100).map((row, idx) => (
            <tr key={idx}>
              {headers.map((header) => (
                <td key={header}>{String(row[header] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
