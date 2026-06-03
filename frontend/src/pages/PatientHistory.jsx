import { Download, Search } from "lucide-react";
import { useEffect, useState } from "react";
import RiskBadge from "../components/ui/RiskBadge.jsx";
import { getHistory } from "../services/api.js";

export default function PatientHistory() {
  const [rows, setRows] = useState([]);
  const [search, setSearch] = useState("");
  const [riskLevel, setRiskLevel] = useState("");

  useEffect(() => {
    getHistory({ search, risk_level: riskLevel || undefined }).then(setRows);
  }, [search, riskLevel]);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-950 dark:text-white">Patient History</h1>
        <p className="text-sm text-slate-500">Search, filter, and reopen previous CAD reports.</p>
      </div>
      <div className="card p-4">
        <div className="flex flex-wrap gap-3">
          <div className="relative min-w-64 flex-1">
            <Search className="absolute left-3 top-2.5 text-slate-400" size={18} />
            <input className="input pl-10" placeholder="Search patient" value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <select className="input max-w-48" value={riskLevel} onChange={(e) => setRiskLevel(e.target.value)}>
            <option value="">All risks</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </div>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="border-b border-slate-200 text-slate-500 dark:border-slate-800">
              <tr>
                <th className="py-3">Patient</th>
                <th>Date</th>
                <th>Risk</th>
                <th>Status</th>
                <th className="text-right">Report</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-b border-slate-100 dark:border-slate-800">
                  <td className="py-4">
                    <p className="font-semibold">{row.patient_name}</p>
                    <p className="text-xs text-slate-500">{row.patient_id || row.id}</p>
                  </td>
                  <td>{new Date(row.created_at).toLocaleDateString()}</td>
                  <td>{row.risk_percentage}%</td>
                  <td><RiskBadge level={row.risk_level} /></td>
                  <td className="text-right">
                    <button className="btn-secondary px-3"><Download size={16} /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
