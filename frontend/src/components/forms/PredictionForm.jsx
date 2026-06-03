import { Mic, Save, Stethoscope } from "lucide-react";
import { useMemo, useRef, useState } from "react";

const defaults = {
  patient_name: "",
  patient_id: "",
  age: "",
  sex: "",
  chest_pain_type: "",
  resting_bp: "",
  cholesterol: "",
  fasting_blood_sugar: "",
  resting_ecg: "",
  max_heart_rate: "",
  exercise_angina: "",
  st_depression: "",
  st_slope: "",
  smoking: "",
  diabetes: "",
  num_major_vessels: "",
  thalassemia: "",
  doctor_notes: "",
};

const numericFields = new Set([
  "age",
  "sex",
  "chest_pain_type",
  "resting_bp",
  "cholesterol",
  "fasting_blood_sugar",
  "resting_ecg",
  "max_heart_rate",
  "exercise_angina",
  "st_depression",
  "st_slope",
  "smoking",
  "diabetes",
  "num_major_vessels",
  "thalassemia",
]);

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{label}</span>
      <div className="mt-1.5">{children}</div>
    </label>
  );
}

export default function PredictionForm({ onSubmit, loading }) {
  const [form, setForm] = useState(defaults);
  const [step, setStep] = useState(0);
  const formRef = useRef(null);
  const progress = useMemo(() => (step === 0 ? 50 : 100), [step]);

  function update(key, value) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function submit(event) {
    event.preventDefault();
    const payload = Object.fromEntries(
      Object.entries(form).map(([key, value]) => [
        key,
        numericFields.has(key) ? Number(value) : value.trim(),
      ]),
    );
    payload.patient_id = payload.patient_id || null;
    payload.doctor_notes = payload.doctor_notes || null;
    onSubmit(payload);
  }

  function updateNumber(key, value) {
    update(key, value === "" ? "" : Number(value));
  }

  function continueToVitals() {
    if (!formRef.current?.reportValidity()) return;
    setStep(1);
  }

  function startVoice() {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) return;
    const recognition = new Recognition();
    recognition.onresult = (event) => update("doctor_notes", `${form.doctor_notes} ${event.results[0][0].transcript}`.trim());
    recognition.start();
  }

  return (
    <form ref={formRef} onSubmit={submit} className="card p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-950 dark:text-white">New CAD Prediction</h2>
          <p className="text-sm text-slate-500">Structured clinical entry with model-ready validation.</p>
        </div>
        <div className="h-2 w-40 rounded-full bg-slate-100 dark:bg-slate-800">
          <div className="h-2 rounded-full bg-clinical-blue transition-all" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {step === 0 ? (
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <Field label="Patient Name">
            <input className="input" required value={form.patient_name} onChange={(e) => update("patient_name", e.target.value)} />
          </Field>
          <Field label="Patient ID">
            <input className="input" value={form.patient_id} onChange={(e) => update("patient_id", e.target.value)} />
          </Field>
          <Field label="Age">
            <input className="input" type="number" min="1" max="120" required value={form.age} onChange={(e) => updateNumber("age", e.target.value)} />
          </Field>
          <Field label="Sex">
            <select className="input" required value={form.sex} onChange={(e) => updateNumber("sex", e.target.value)}>
              <option value="">Select sex</option>
              <option value={1}>Male</option>
              <option value={0}>Female</option>
            </select>
          </Field>
          <Field label="Smoking">
            <select className="input" required value={form.smoking} onChange={(e) => updateNumber("smoking", e.target.value)}>
              <option value="">Select smoking status</option>
              <option value={0}>No</option>
              <option value={1}>Yes</option>
            </select>
          </Field>
          <Field label="Diabetes">
            <select className="input" required value={form.diabetes} onChange={(e) => updateNumber("diabetes", e.target.value)}>
              <option value="">Select diabetes status</option>
              <option value={0}>No</option>
              <option value={1}>Yes</option>
            </select>
          </Field>
        </div>
      ) : (
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <Field label="Chest Pain Type">
            <select className="input" required value={form.chest_pain_type} onChange={(e) => updateNumber("chest_pain_type", e.target.value)}>
              <option value="">Select chest pain type</option>
              <option value={0}>Typical angina</option>
              <option value={1}>Atypical angina</option>
              <option value={2}>Non-anginal pain</option>
              <option value={3}>Asymptomatic</option>
            </select>
          </Field>
          <Field label="Resting Blood Pressure">
            <input className="input" type="number" min="60" max="260" required value={form.resting_bp} onChange={(e) => updateNumber("resting_bp", e.target.value)} />
          </Field>
          <Field label="Cholesterol">
            <input className="input" type="number" min="0" max="700" required value={form.cholesterol} onChange={(e) => updateNumber("cholesterol", e.target.value)} />
          </Field>
          <Field label="Max Heart Rate">
            <input className="input" type="number" min="40" max="260" required value={form.max_heart_rate} onChange={(e) => updateNumber("max_heart_rate", e.target.value)} />
          </Field>
          <Field label="Fasting Blood Sugar">
            <select className="input" required value={form.fasting_blood_sugar} onChange={(e) => updateNumber("fasting_blood_sugar", e.target.value)}>
              <option value="">Select fasting blood sugar</option>
              <option value={0}>Below 120 mg/dl</option>
              <option value={1}>Above 120 mg/dl</option>
            </select>
          </Field>
          <Field label="ECG Results">
            <select className="input" required value={form.resting_ecg} onChange={(e) => updateNumber("resting_ecg", e.target.value)}>
              <option value="">Select ECG result</option>
              <option value={0}>Normal</option>
              <option value={1}>ST-T abnormality</option>
              <option value={2}>Left ventricular hypertrophy</option>
            </select>
          </Field>
          <Field label="Exercise Angina">
            <select className="input" required value={form.exercise_angina} onChange={(e) => updateNumber("exercise_angina", e.target.value)}>
              <option value="">Select exercise angina</option>
              <option value={0}>No</option>
              <option value={1}>Yes</option>
            </select>
          </Field>
          <Field label="Oldpeak">
            <input className="input" type="number" step="0.1" min="0" max="10" required value={form.st_depression} onChange={(e) => updateNumber("st_depression", e.target.value)} />
          </Field>
          <Field label="ST Slope">
            <select className="input" required value={form.st_slope} onChange={(e) => updateNumber("st_slope", e.target.value)}>
              <option value="">Select ST slope</option>
              <option value={0}>Upsloping</option>
              <option value={1}>Flat</option>
              <option value={2}>Downsloping</option>
            </select>
          </Field>
          <Field label="Major Vessels">
            <select className="input" required value={form.num_major_vessels} onChange={(e) => updateNumber("num_major_vessels", e.target.value)}>
              <option value="">Select vessel count</option>
              <option value={0}>0</option>
              <option value={1}>1</option>
              <option value={2}>2</option>
              <option value={3}>3</option>
              <option value={4}>4</option>
            </select>
          </Field>
          <Field label="Thalassemia">
            <select className="input" required value={form.thalassemia} onChange={(e) => updateNumber("thalassemia", e.target.value)}>
              <option value="">Select thalassemia result</option>
              <option value={0}>Unknown</option>
              <option value={1}>Normal</option>
              <option value={2}>Fixed defect</option>
              <option value={3}>Reversible defect</option>
            </select>
          </Field>
          <Field label="Doctor Notes">
            <div className="flex gap-2">
              <textarea className="input min-h-24" value={form.doctor_notes} onChange={(e) => update("doctor_notes", e.target.value)} />
              <button type="button" className="btn-secondary self-start px-3" onClick={startVoice} aria-label="Voice input">
                <Mic size={18} />
              </button>
            </div>
          </Field>
        </div>
      )}

      <div className="mt-6 flex justify-between">
        <button type="button" className="btn-secondary" disabled={step === 0} onClick={() => setStep(0)}>
          Back
        </button>
        {step === 0 ? (
          <button type="button" className="btn-primary" onClick={continueToVitals}>
            <Stethoscope size={18} /> Continue
          </button>
        ) : (
          <button className="btn-primary" disabled={loading}>
            <Save size={18} /> {loading ? "Analyzing..." : "Predict CAD Risk"}
          </button>
        )}
      </div>
    </form>
  );
}
