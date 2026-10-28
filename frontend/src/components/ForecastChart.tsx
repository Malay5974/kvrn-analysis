import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { AnalysisPoint } from "../api";
import { formatChartTime, formatMw } from "../analysis";

export function ForecastChart({ points }: { points: AnalysisPoint[] }) {
  return <div className="chart-frame" aria-label="Wind generation forecast versus actual chart">
    <ResponsiveContainer width="100%" height={360}>
      <LineChart data={points} margin={{ top: 12, right: 12, bottom: 4, left: 0 }}>
        <CartesianGrid stroke="#dce5df" strokeDasharray="3 5" vertical={false} />
        <XAxis dataKey="delivery_time" tickFormatter={formatChartTime} minTickGap={42} tick={{ fill: "#64736d", fontSize: 11 }} tickLine={false} axisLine={{ stroke: "#c9d5cf" }} />
        <YAxis tickFormatter={(value: number) => `${Math.round(value / 1000)}k`} width={45} tick={{ fill: "#64736d", fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip labelFormatter={(value) => new Intl.DateTimeFormat("en-GB", { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" }).format(new Date(String(value)))} formatter={(value, name) => [formatMw(Number(value)), name]} contentStyle={{ borderRadius: 12, border: "1px solid #d7e1dc", boxShadow: "0 14px 36px #1a3a2c18" }} />
        <Legend iconType="plainline" wrapperStyle={{ paddingTop: 16, fontSize: 12 }} />
        <Line name="Forecast" type="monotone" dataKey="forecast_mw" stroke="#b76035" strokeWidth={2.2} dot={false} activeDot={{ r: 4 }} connectNulls={false} />
        <Line name="Actual" type="monotone" dataKey="actual_mw" stroke="#16745b" strokeWidth={2.2} dot={false} activeDot={{ r: 4 }} connectNulls={false} />
      </LineChart>
    </ResponsiveContainer>
  </div>;
}
