import { Activity, ArrowRight, LockKeyhole } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";

export default function ResetPassword() {
  const { session, updatePassword, signOut, loading } = useAuth();
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [saving, setSaving] = useState(false);

  if (loading) {
    return <div className="grid min-h-screen place-items-center text-clinical-ink">Loading CardioSense...</div>;
  }

  if (!session) {
    return <Navigate to="/forgot-password" replace />;
  }

  async function submit(event) {
    event.preventDefault();
    if (password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }
    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    setSaving(true);
    try {
      await updatePassword(password);
      await signOut();
      toast.success("Password updated. Please sign in again.");
      navigate("/login", { replace: true });
    } catch (error) {
      toast.error(error.message || "Password update failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="grid min-h-screen place-items-center bg-clinical-cloud px-6 py-10 dark:bg-slate-950">
      <form onSubmit={submit} className="card w-full max-w-md p-6">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-lg bg-clinical-blue text-white">
            <Activity />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-950 dark:text-white">CardioSense</h1>
            <p className="text-sm text-slate-500">Set a new password</p>
          </div>
        </div>

        <div className="mt-6 space-y-4">
          <label className="block">
            <span className="text-sm font-semibold">New Password</span>
            <div className="relative mt-1.5">
              <LockKeyhole className="absolute left-3 top-2.5 text-slate-400" size={18} />
              <input
                className="input pl-10"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </div>
          </label>
          <label className="block">
            <span className="text-sm font-semibold">Confirm Password</span>
            <div className="relative mt-1.5">
              <LockKeyhole className="absolute left-3 top-2.5 text-slate-400" size={18} />
              <input
                className="input pl-10"
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
              />
            </div>
          </label>
        </div>

        <button className="btn-primary mt-6 w-full" disabled={saving}>
          {saving ? "Updating..." : "Update password"}
          <ArrowRight size={18} />
        </button>
      </form>
    </div>
  );
}
