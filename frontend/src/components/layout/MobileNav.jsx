import { BarChart3, ClipboardPlus, History, LayoutDashboard } from "lucide-react";
import { NavLink } from "react-router-dom";

const items = [
  { label: "Home", to: "/", icon: LayoutDashboard },
  { label: "Predict", to: "/prediction", icon: ClipboardPlus },
  { label: "History", to: "/history", icon: History },
  { label: "Analytics", to: "/analytics", icon: BarChart3 },
];

export default function MobileNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-30 grid grid-cols-4 border-t border-slate-200 bg-white px-2 py-2 dark:border-slate-800 dark:bg-slate-950 lg:hidden">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === "/"}
          className={({ isActive }) =>
            `flex flex-col items-center gap-1 rounded-lg py-1.5 text-[11px] font-semibold ${
              isActive ? "text-clinical-blue" : "text-slate-500"
            }`
          }
        >
          <item.icon size={18} />
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
