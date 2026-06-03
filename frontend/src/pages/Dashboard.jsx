import { AlertTriangle, ClipboardCheck, Gauge, Users } from "lucide-react";
import { useEffect, useState } from "react";
import MetricCard from "../components/ui/MetricCard.jsx";
import { RiskPie, TrendChart } from "../components/charts/DashboardCharts.jsx";
import { getAnalytics } from "../services/api.js";

export default function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  useEffect(() => {
    getAnalytics().then(setAnalytics).catch(() => setAnalytics(null));
  }, []);
  const summary = analytics?.summary || { total_patients: 0, total_predictions: 0, high_risk_cases: 0, average_risk_score: 0 };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950 dark:text-white">Clinical Dashboard</h1>
        <p className="text-sm text-slate-500">Live CAD risk intelligence across your patient workflow.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Total Patients" value={summary.total_patients} change="+12 this month" icon={Users} tone="blue" />
        <MetricCard title="Total Predictions" value={summary.total_predictions} change="Model service online" icon={ClipboardCheck} tone="teal" />
        <MetricCard title="High Risk Cases" value={summary.high_risk_cases} change="Needs clinical review" icon={AlertTriangle} tone="rose" />
        <MetricCard title="Average Risk Score" value={`${summary.average_risk_score}%`} change="Across all reports" icon={Gauge} tone="amber" />
      </div>
      <div className="grid gap-4 xl:grid-cols-[1.4fr_0.8fr]">
        <TrendChart data={analytics?.monthly_trends || []} />
        <RiskPie data={analytics?.risk_distribution || []} />
      </div>
    </div>
  );
}
