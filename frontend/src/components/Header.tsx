import React from "react";
import { Bell, User, Sparkles, Download, RefreshCw } from "lucide-react";

interface HeaderProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  onRunAiCheck: () => void;
  onExport: () => void;
  isRunning: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  setCurrentTab,
  onRunAiCheck,
  onExport,
  isRunning,
}) => {
  const subTabs = [
    { id: "dashboard", label: "Overview" },
    { id: "reconciliation", label: "Batch Processing" },
    { id: "audit", label: "History" },
  ];

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-10">
      {/* Title & Navigation Subtabs */}
      <div className="flex items-center gap-8">
        <h2 className="font-bold text-slate-900 text-lg">
          SettleX
        </h2>
        <div className="flex items-center gap-6">
          {subTabs.map((sub) => {
            const isActive = currentTab === sub.id;
            return (
              <button
                key={sub.id}
                onClick={() => setCurrentTab(sub.id)}
                className={`text-sm font-medium transition-colors pb-1 border-b-2 ${
                  isActive
                    ? "text-slate-900 border-slate-900 font-semibold"
                    : "text-slate-400 border-transparent hover:text-slate-600"
                }`}
              >
                {sub.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3">
        <button
          onClick={onRunAiCheck}
          disabled={isRunning}
          className="bg-black hover:bg-slate-800 text-white text-xs font-semibold px-4 py-2 rounded-md flex items-center gap-2 shadow-sm transition-all disabled:opacity-60"
        >
          {isRunning ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-400" />
          ) : (
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
          )}
          <span>Run AI Check</span>
        </button>

        <button
          onClick={onExport}
          className="border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold px-3.5 py-2 rounded-md flex items-center gap-1.5 transition-colors"
        >
          <Download className="w-3.5 h-3.5 text-slate-500" />
          Export
        </button>

        <button className="p-2 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100">
          <Bell className="w-4 h-4" />
        </button>

        <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold ring-2 ring-slate-100">
          <User className="w-4 h-4 text-emerald-300" />
        </div>
      </div>
    </header>
  );
};
