import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import type { VizType } from "../../types";

interface ChartViewProps {
  rows: Record<string, unknown>[];
  vizType: VizType;
}

const COLORS = ["#2f7a56", "#9a5d2d", "#5f7943", "#b23a34", "#8d6f34"];

export function ChartView({ rows, vizType }: ChartViewProps) {
  if (rows.length === 0) {
    return (
      <div className="empty-state">
        <p>Insufficient data for visualization.</p>
        <p className="subtle-text">Run a query that returns numeric data.</p>
      </div>
    );
  }

  const keys = Object.keys(rows[0]);
  const xKey = keys[0] as string;
  const yKey = keys.find((k) => typeof rows[0][k] === "number") ?? keys[1] ?? keys[0];

  const tooltipStyle = {
    backgroundColor: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    color: 'var(--text-main)',
    boxShadow: 'var(--shadow-md)',
    fontSize: '0.8125rem'
  };

  const axisStyle = {
    stroke: 'var(--text-muted)',
    fontSize: 11,
    tickLine: false,
    axisLine: { stroke: 'var(--border)' }
  };

  if (vizType === "pie") {
    return (
      <div className="chart-canvas">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={rows}
              dataKey={yKey}
              nameKey={xKey}
              outerRadius={100}
              innerRadius={55}
              paddingAngle={2}
              stroke="var(--surface)"
              strokeWidth={2}
            >
              {rows.map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={tooltipStyle} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (vizType === "line") {
    return (
      <div className="chart-canvas">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={rows}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
            <XAxis dataKey={xKey} {...axisStyle} />
            <YAxis {...axisStyle} />
            <Tooltip contentStyle={tooltipStyle} />
            <Line
              type="monotone"
              dataKey={yKey}
              stroke="var(--primary)"
              strokeWidth={2.5}
              dot={{ fill: 'var(--surface)', stroke: 'var(--primary)', strokeWidth: 2, r: 3.5 }}
              activeDot={{ r: 5, strokeWidth: 0, fill: 'var(--primary)' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return (
    <div className="chart-canvas">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
          <XAxis dataKey={xKey} {...axisStyle} />
          <YAxis {...axisStyle} />
          <Tooltip contentStyle={tooltipStyle} cursor={{ fill: 'var(--surface-hover)' }} />
          <Bar dataKey={yKey} fill="var(--primary)" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
