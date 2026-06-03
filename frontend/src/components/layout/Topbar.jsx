import { LogOut, Moon, Search, Sun } from "lucide-react";
import { useAuth } from "../../hooks/useAuth.jsx";
import { useDarkMode } from "../../hooks/useDarkMode.js";

export default function Topbar() {
  const { user, signOut } = useAuth();
  const { dark, setDark } = useDarkMode();
  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/85 px-4 py-3 backdrop-blur dark:border-slate-800 dark:bg-slate-950/85 lg:px-8">
      <div className="flex items-center justify-between gap-4">
        <div className="relative hidden w-full max-w-md md:block">
          <Search className="absolute left-3 top-2.5 text-slate-400" size={18} />
          <input className="input pl-10" placeholder="Search patients, reports, case IDs" />
        </div>
        <div className="ml-auto flex items-center gap-2">
          <button className="btn-secondary px-3" onClick={() => setDark(!dark)} aria-label="Toggle theme">
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <div className="hidden text-right sm:block">
            <p className="text-sm font-semibold text-slate-900 dark:text-white">{user?.user_metadata?.full_name || "Clinical User"}</p>
            <p className="text-xs text-slate-500">{user?.email}</p>
          </div>
          <button className="btn-secondary px-3" onClick={signOut} aria-label="Sign out">
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </header>
  );
}
