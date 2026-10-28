import { Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatMw, type DailyError } from "../analysis";

export function ErrorChart({ days }: { days: DailyError[] }) {
  return <div className="chart-frame" aria-label="Daily average forecast error chart">
    <ResponsiveContainer width="100%" height={270}>
      <BarChart data={days} margin={{ top: 12, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid stroke="#dce5df" strokeDasharray="3 5" vertical={false} />
        <XAxis dataKey="label" minTickGap={24} tick={{ fill: "#64736d", fontSize: 11 }} tickLine={false} axisLine={{ stroke: "#c9d5cf" }} />
        <YAxis tickFormatter={(value: number) => `${Math.round(value / 1000)}k`} width={42} tick={{ fill: "#64736d", fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip formatter={(value) => [formatMw(Number(value)), "Daily bias"]} />
        <ReferenceLine y={0} stroke="#8c9a94" />
        <Bar dataKey="bias" radius={[4, 4, 0, 0]} maxBarSize={24}>{days.map((day) => <Cell key={day.date} fill={day.bias >= 0 ? "#c06b3d" : "#2c846d"} />)}</Bar>
      </BarChart>
    </ResponsiveContainer>
  </div>;
}
