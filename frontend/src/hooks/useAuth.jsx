import { createContext, useContext, useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { attachAuthToken } from "../services/api";
import { supabase, supabaseConfigured } from "../services/supabaseClient";

const AuthContext = createContext(null);

const demoSession = {
  access_token: "local-demo-token",
  user: {
    id: "local-demo-user",
    email: "doctor@cardiosense.local",
    user_metadata: { role: "doctor", full_name: "Demo Doctor" },
  },
};

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    const stored = localStorage.getItem("cardiosense-demo-session");
    return stored ? demoSession : null;
  });
  const [loading, setLoading] = useState(Boolean(supabaseConfigured));
  const [passwordRecovery, setPasswordRecovery] = useState(false);

  useEffect(() => {
    if (!supabaseConfigured) {
      attachAuthToken(session?.access_token);
      setLoading(false);
      return;
    }

    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      attachAuthToken(data.session?.access_token);
      setLoading(false);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((event, nextSession) => {
      if (event === "PASSWORD_RECOVERY") {
        setPasswordRecovery(true);
      }
      setSession(nextSession);
      attachAuthToken(nextSession?.access_token);
    });

    return () => listener.subscription.unsubscribe();
  }, []);

  async function signIn(email, password) {
    if (!supabaseConfigured) {
      localStorage.setItem("cardiosense-demo-session", "true");
      setSession(demoSession);
      attachAuthToken(demoSession.access_token);
      toast.success("Demo session started");
      return;
    }
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
  }

  async function signUp(email, password, role, fullName) {
    if (!supabaseConfigured) {
      return signIn(email, password);
    }
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { role, full_name: fullName } },
    });
    if (error) throw error;
  }

  async function resetPassword(email) {
    if (!supabaseConfigured) {
      toast.success("Demo mode: password reset simulated");
      return;
    }
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`,
    });
    if (error) throw error;
  }

  async function updatePassword(password) {
    if (!supabaseConfigured) {
      toast.success("Demo mode: password updated");
      return;
    }
    const { error } = await supabase.auth.updateUser({ password });
    if (error) throw error;
    setPasswordRecovery(false);
  }

  async function signOut() {
    if (supabaseConfigured) await supabase.auth.signOut();
    localStorage.removeItem("cardiosense-demo-session");
    setPasswordRecovery(false);
    setSession(null);
    attachAuthToken(null);
  }

  const value = useMemo(
    () => ({
      session,
      user: session?.user,
      loading,
      passwordRecovery,
      signIn,
      signUp,
      resetPassword,
      updatePassword,
      signOut,
      supabaseConfigured,
    }),
    [session, loading, passwordRecovery]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
