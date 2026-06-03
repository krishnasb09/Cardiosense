import { Activity, ArrowRight, LockKeyhole, Mail, UserRound } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";

export default function AuthPage({ mode }) {
  const { session, signIn, signUp, resetPassword, supabaseConfigured } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("doctor");
  const [loading, setLoading] = useState(false);

  if (session) return <Navigate to="/" replace />;

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    try {
      if (mode === "signup") {
        await signUp(email, password, role, fullName);
        toast.success("Account created. Check email if confirmation is enabled.");
      } else if (mode === "forgot") {
        await resetPassword(email);
        toast.success("Password reset link sent. Check your email.");
        return;
      } else {
        await signIn(email, password);
      }
      navigate("/");
    } catch (error) {
      toast.error(error.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen bg-slate-950 lg:grid-cols-[1.05fr_0.95fr]">
      <section className="relative overflow-hidden bg-[radial-gradient(circle_at_top_left,#1d4ed8_0,#0f172a_38%,#0a0f1f_100%)] px-6 py-10 text-white lg:px-14">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-lg bg-white/15">
            <Activity />
          </div>
          <div>
            <h1 className="text-xl font-bold">CardioSense</h1>
            <p className="text-sm text-blue-100">AI-based CAD prediction system</p>
          </div>
        </div>
        <div className="mt-20 max-w-2xl">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-200">Clinical decision intelligence</p>
          <h2 className="mt-4 text-4xl font-bold leading-tight lg:text-6xl">Professional CAD risk screening for modern care teams</h2>
          <p className="mt-6 text-lg leading-8 text-slate-200">
            Enter patient clinical values, generate CAD risk predictions, and review saved patient history from one secure dashboard.
          </p>
        </div>
      </section>
      <section className="grid place-items-center bg-clinical-cloud px-6 py-10 dark:bg-slate-950">
        <form onSubmit={submit} className="card w-full max-w-md p-6">
          <h2 className="text-2xl font-bold text-slate-950 dark:text-white">
            {mode === "signup" ? "Create clinical account" : mode === "forgot" ? "Reset password" : "Welcome back"}
          </h2>
          <p className="mt-2 text-sm text-slate-500">
            {supabaseConfigured ? "Secure session powered by Supabase Auth." : "Demo mode is active until Supabase keys are added."}
          </p>

          <div className="mt-6 space-y-4">
            {mode === "signup" && (
              <label className="block">
                <span className="text-sm font-semibold">Full Name</span>
                <div className="relative mt-1.5">
                  <UserRound className="absolute left-3 top-2.5 text-slate-400" size={18} />
                  <input className="input pl-10" placeholder="Enter full name" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
                </div>
              </label>
            )}
            <label className="block">
              <span className="text-sm font-semibold">Email</span>
              <div className="relative mt-1.5">
                <Mail className="absolute left-3 top-2.5 text-slate-400" size={18} />
                <input className="input pl-10" type="email" placeholder="Enter email address" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
            </label>
            {mode !== "forgot" && (
              <label className="block">
                <span className="text-sm font-semibold">Password</span>
                <div className="relative mt-1.5">
                  <LockKeyhole className="absolute left-3 top-2.5 text-slate-400" size={18} />
                  <input className="input pl-10" type="password" placeholder="Enter password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                </div>
              </label>
            )}
            {mode === "signup" && (
              <label className="block">
                <span className="text-sm font-semibold">Role</span>
                <select className="input mt-1.5" value={role} onChange={(e) => setRole(e.target.value)}>
                  <option value="doctor">Doctor</option>
                  <option value="admin">Admin</option>
                  <option value="patient">Patient</option>
                </select>
              </label>
            )}
          </div>

          <button className="btn-primary mt-6 w-full" disabled={loading}>
            {loading ? "Please wait..." : mode === "forgot" ? "Send reset link" : mode === "signup" ? "Create account" : "Sign in"}
            <ArrowRight size={18} />
          </button>
          <div className="mt-5 flex flex-wrap justify-between gap-3 text-sm">
            <Link className="font-semibold text-clinical-blue" to={mode === "signup" ? "/login" : "/signup"}>
              {mode === "signup" ? "Have an account?" : "Create account"}
            </Link>
            <Link className="font-semibold text-slate-500" to="/forgot-password">Forgot password?</Link>
          </div>
        </form>
      </section>
    </div>
  );
}
