import { Navigate, Route, Routes } from "react-router-dom";
import AuthPage from "./pages/AuthPage.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import NewPrediction from "./pages/NewPrediction.jsx";
import PatientHistory from "./pages/PatientHistory.jsx";
import Analytics from "./pages/Analytics.jsx";
import ResetPassword from "./pages/ResetPassword.jsx";
import AppLayout from "./layouts/AppLayout.jsx";
import { useAuth } from "./hooks/useAuth.jsx";

function ProtectedRoute({ children }) {
  const { session, loading, passwordRecovery } = useAuth();
  if (loading) return <div className="grid min-h-screen place-items-center text-clinical-ink">Loading CardioSense...</div>;
  if (passwordRecovery) return <Navigate to="/reset-password" replace />;
  return session ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage mode="login" />} />
      <Route path="/signup" element={<AuthPage mode="signup" />} />
      <Route path="/forgot-password" element={<AuthPage mode="forgot" />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="prediction" element={<NewPrediction />} />
        <Route path="history" element={<PatientHistory />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="reports" element={<Navigate to="/" replace />} />
        <Route path="settings" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
