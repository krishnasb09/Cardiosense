import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const colors = ["#0f766e", "#f59e0b", "#e11d48"];

export function TrendChart({ data = [] }) {
  return (
    <div className="card p-5">
      <h2 className="text-base font-bold text-slate-950 dark:text-white">Monthly Risk Trends</h2>
      <div className="mt-4 h-72">
        <ResponsiveContainer>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Area dataKey="low" stackId="1" stroke="#0f766e" fill="#99f6e4" />
            <Area dataKey="medium" stackId="1" stroke="#f59e0b" fill="#fde68a" />
            <Area dataKey="high" stackId="1" stroke="#e11d48" fill="#fecdd3" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function RiskPie({ data = [] }) {
  return (
    <div className="card p-5">
      <h2 className="text-base font-bold text-slate-950 dark:text-white">Risk Distribution</h2>
      <div className="mt-4 h-72">
        <ResponsiveContainer>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" outerRadius={92} label>
              {data.map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function AgeBar({ data = [] }) {
  return (
    <div className="card p-5">
      <h2 className="text-base font-bold text-slate-950 dark:text-white">Age Distribution</h2>
      <div className="mt-4 h-72">
        <ResponsiveContainer>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="range" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="patients" fill="#2563eb" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
