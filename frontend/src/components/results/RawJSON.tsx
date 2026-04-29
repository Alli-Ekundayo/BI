interface RawJsonProps {
  rows: Record<string, unknown>[];
}

export function RawJSON({ rows }: RawJsonProps) {
  return (
    <pre className="raw-json-view">
      {JSON.stringify(rows, null, 2)}
    </pre>
  );
}
