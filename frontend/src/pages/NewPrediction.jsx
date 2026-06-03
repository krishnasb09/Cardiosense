import { motion } from "framer-motion";
import { Download, FileText } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import PredictionForm from "../components/forms/PredictionForm.jsx";
import { FeatureImportance, RiskGauge } from "../components/charts/ResultVisuals.jsx";
import RiskBadge from "../components/ui/RiskBadge.jsx";
import { downloadReport, predictCad } from "../services/api.js";

export default function NewPrediction() {
  const [loading, setLoading] = useState(false);
  const [patient, setPatient] = useState(null);
  const [result, setResult] = useState(null);

  async function handleSubmit(form) {
    setLoading(true);
    try {
      const response = await predictCad(form);
      setPatient(form);
      setResult(response);
      toast.success("CAD risk prediction generated");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Prediction failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleDownload() {
    const blob = await downloadReport({ patient, prediction: result, doctor_name: "CardioSense Doctor" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "cardiosense-report.pdf";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <PredictionForm onSubmit={handleSubmit} loading={loading} />
      <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="card p-5">
        {!result ? (
          <div className="grid min-h-[520px] place-items-center text-center">
            <div>
              <FileText className="mx-auto text-clinical-blue" size={44} />
              <h2 className="mt-4 text-xl font-bold text-slate-950 dark:text-white">Prediction result appears here</h2>
              <p className="mt-2 max-w-md text-sm text-slate-500">Submit patient vitals to view risk score, SHAP factors, recommendations, and report export.</p>
            </div>
          </div>
        ) : (
          <div className="space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm text-slate-500">{result.patient_name}</p>
                <h2 className="text-2xl font-bold text-slate-950 dark:text-white">CAD Risk Assessment</h2>
              </div>
              <RiskBadge level={result.risk_level} />
            </div>
            <RiskGauge value={result.risk_percentage} />
            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
                <p className="text-sm text-slate-500">Confidence</p>
                <p className="text-2xl font-bold">{result.confidence_score}%</p>
              </div>
              <div className="rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
                <p className="text-sm text-slate-500">Correlated Factors</p>
                <p className="text-sm font-semibold">{result.correlated_factors.join(", ")}</p>
              </div>
            </div>
            <FeatureImportance data={result.feature_importance} />
            <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-800">
              <h3 className="font-bold">Clinical Suggestions</h3>
              <ul className="mt-2 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                {result.recommendations.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
            <button className="btn-primary" onClick={handleDownload}>
              <Download size={18} /> Download PDF Report
            </button>
          </div>
        )}
      </motion.section>
    </div>
  );
}
