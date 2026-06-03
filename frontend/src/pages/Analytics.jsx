import { useEffect, useState } from "react";
import { AgeBar, RiskPie, TrendChart } from "../components/charts/DashboardCharts.jsx";
import { getAnalytics } from "../services/api.js";

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  useEffect(() => {
    getAnalytics().then(setAnalytics);
  }, []);
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-950 dark:text-white">Analytics</h1>
        <p className="text-sm text-slate-500">Population-level CAD patterns and risk correlations.</p>
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        <TrendChart data={analytics?.monthly_trends || []} />
        <AgeBar data={analytics?.age_distribution || []} />
        <RiskPie data={analytics?.risk_distribution || []} />
        <div className="card p-5">
          <h2 className="text-base font-bold text-slate-950 dark:text-white">Cholesterol Correlation</h2>
          <div className="mt-6 space-y-4">
            {(analytics?.cholesterol_correlation || []).map((item) => (
              <div key={item.cholesterol}>
                <div className="mb-1 flex justify-between text-sm">
                  <span>{item.cholesterol} mg/dl</span>
                  <strong>{item.risk}% risk</strong>
                </div>
                <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800">
                  <div className="h-2 rounded-full bg-clinical-rose" style={{ width: `${item.risk}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
