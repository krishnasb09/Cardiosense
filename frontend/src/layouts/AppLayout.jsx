import { Outlet } from "react-router-dom";
import MobileNav from "../components/layout/MobileNav.jsx";
import Sidebar from "../components/layout/Sidebar.jsx";
import Topbar from "../components/layout/Topbar.jsx";

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-clinical-cloud dark:bg-slate-950">
      <div className="flex">
        <Sidebar />
        <main className="min-w-0 flex-1">
          <Topbar />
          <div className="px-4 pb-24 pt-6 lg:px-8 lg:pb-6">
            <Outlet />
          </div>
        </main>
      </div>
      <MobileNav />
    </div>
  );
}
