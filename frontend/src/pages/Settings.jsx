import { Bell, Database, KeyRound } from "lucide-react";
import { useAuth } from "../hooks/useAuth.jsx";

export default function Settings() {
  const { supabaseConfigured } = useAuth();
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-950 dark:text-white">Settings</h1>
        <p className="text-sm text-slate-500">Environment, security, and clinical workflow preferences.</p>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="card p-5">
          <Database className="text-clinical-blue" />
          <h2 className="mt-4 font-bold">Supabase</h2>
          <p className="mt-2 text-sm text-slate-500">{supabaseConfigured ? "Connected" : "Demo mode: add env keys to enable cloud auth and history."}</p>
        </div>
        <div className="card p-5">
          <KeyRound className="text-clinical-teal" />
          <h2 className="mt-4 font-bold">Protected Routes</h2>
          <p className="mt-2 text-sm text-slate-500">Doctor and admin-only prediction endpoints are enforced by FastAPI middleware.</p>
        </div>
        <div className="card p-5">
          <Bell className="text-clinical-amber" />
          <h2 className="mt-4 font-bold">Realtime Updates</h2>
          <p className="mt-2 text-sm text-slate-500">Supabase realtime channels can be enabled for live case queues.</p>
        </div>
      </div>
    </div>
  );
}
