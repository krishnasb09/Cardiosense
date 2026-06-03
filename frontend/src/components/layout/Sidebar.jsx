import { Activity, BarChart3, ClipboardPlus, History, LayoutDashboard } from "lucide-react";
import { NavLink } from "react-router-dom";

const items = [
  { label: "Dashboard", to: "/", icon: LayoutDashboard },
  { label: "New Prediction", to: "/prediction", icon: ClipboardPlus },
  { label: "Patient History", to: "/history", icon: History },
  { label: "Analytics", to: "/analytics", icon: BarChart3 },
];

export default function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-72 border-r border-slate-200 bg-white px-4 py-5 dark:border-slate-800 dark:bg-slate-950 lg:block">
      <div className="flex items-center gap-3 px-2">
        <div className="grid h-11 w-11 place-items-center rounded-lg bg-clinical-blue text-white">
          <Activity size={24} />
        </div>
        <div>
          <h1 className="text-lg font-bold text-slate-950 dark:text-white">CardioSense</h1>
          <p className="text-xs text-slate-500">CAD intelligence</p>
        </div>
      </div>
      <nav className="mt-8 space-y-1">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                isActive
                  ? "bg-blue-50 text-clinical-blue dark:bg-blue-950 dark:text-blue-300"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900"
              }`
            }
          >
            <item.icon size={18} />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
