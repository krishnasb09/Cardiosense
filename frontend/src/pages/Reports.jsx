import { FileText, ShieldCheck } from "lucide-react";

export default function Reports() {
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-950 dark:text-white">Reports</h1>
        <p className="text-sm text-slate-500">PDF exports generated from prediction results include vitals, score, explainability, and notes.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="card p-5">
          <FileText className="text-clinical-blue" />
          <h2 className="mt-4 text-lg font-bold">Medical PDF Template</h2>
          <p className="mt-2 text-sm text-slate-500">Professional report layout with risk summary, clinical inputs, SHAP drivers, and doctor guidance.</p>
        </div>
        <div className="card p-5">
          <ShieldCheck className="text-clinical-teal" />
          <h2 className="mt-4 text-lg font-bold">Audit-ready History</h2>
          <p className="mt-2 text-sm text-slate-500">When Supabase is configured, report metadata and prediction history are stored centrally.</p>
        </div>
      </div>
    </div>
  );
}
