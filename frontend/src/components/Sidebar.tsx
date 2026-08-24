import React from "react";
import {
  LayoutDashboard,
  FileCheck2,
  AlertOctagon,
  BarChart3,
  History,
  Settings,
  HelpCircle,
  Plus,
  Layers,
} from "lucide-react";

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  onNewJob: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab, onNewJob }) => {
  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "reconciliation", label: "Reconciliation", icon: FileCheck2 },
    { id: "exceptions", label: "Exceptions", icon: AlertOctagon },
    { id: "evaluation", label: "Evaluation", icon: BarChart3 },
    { id: "audit", label: "Audit Log", icon: History },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between h-screen fixed left-0 top-0 select-none z-20">
      <div>
        {/* Brand Header */}
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center text-white shadow-sm">
            <Layers className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h1 className="font-bold text-base tracking-tight text-slate-900 leading-none">
              SettleX
            </h1>
            <p className="text-[11px] text-slate-400 font-medium tracking-wide mt-0.5">
              AI Financial Intelligence
            </p>
          </div>
        </div>

        {/* Action Button */}
        <div className="px-5 mb-6">
          <button
            onClick={onNewJob}
            className="w-full bg-black hover:bg-slate-800 text-white font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 text-sm shadow transition-all duration-150 active:scale-[0.98]"
          >
            <Plus className="w-4 h-4 text-emerald-400" />
            + New Job
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="px-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`w-full flex items-center justify-between px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "text-slate-950 font-semibold bg-slate-50 relative"
                    : "text-slate-500 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? "text-emerald-700" : "text-slate-400"
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {isActive && (
                  <div className="w-1.5 h-5 bg-emerald-700 rounded-full" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Navigation */}
      <div className="p-4 border-t border-slate-100 space-y-1">
        <button
          onClick={() => setCurrentTab("settings")}
          className="w-full flex items-center gap-3 px-4 py-2 text-sm font-medium text-slate-500 hover:text-slate-900 rounded-lg hover:bg-slate-50"
        >
          <Settings className="w-4 h-4 text-slate-400" />
          Settings
        </button>
        <button className="w-full flex items-center gap-3 px-4 py-2 text-sm font-medium text-slate-500 hover:text-slate-900 rounded-lg hover:bg-slate-50">
          <HelpCircle className="w-4 h-4 text-slate-400" />
          Support
        </button>
      </div>
    </aside>
  );
};
