import { Bar, BarChart, CartesianGrid, Cell, RadialBar, RadialBarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function RiskGauge({ value = 0 }) {
  const color = value >= 70 ? "#e11d48" : value >= 40 ? "#f59e0b" : "#0f766e";
  return (
    <div className="h-64">
      <ResponsiveContainer>
        <RadialBarChart innerRadius="72%" outerRadius="100%" data={[{ name: "Risk", value, fill: color }]} startAngle={180} endAngle={0}>
          <RadialBar minAngle={15} background clockWise dataKey="value" cornerRadius={8} />
          <text x="50%" y="54%" textAnchor="middle" dominantBaseline="middle" className="fill-slate-950 text-4xl font-bold dark:fill-white">
            {value}%
          </text>
        </RadialBarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function FeatureImportance({ data = [] }) {
  const chartData = data.map((item) => ({ ...item, abs: Math.abs(item.importance) }));
  return (
    <div className="h-80">
      <ResponsiveContainer>
        <BarChart data={chartData} layout="vertical" margin={{ left: 38 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis type="number" />
          <YAxis dataKey="feature" type="category" width={112} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="abs" radius={[0, 6, 6, 0]}>
            {chartData.map((item, index) => <Cell key={index} fill={item.importance >= 0 ? "#e11d48" : "#0f766e"} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
