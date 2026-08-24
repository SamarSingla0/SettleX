import type React from "react";
import type { SystemHealth } from "../types";
import { EmptyState } from "../components/EmptyState";

export const SettingsView: React.FC<{ health: SystemHealth | null }> = ({ health }) => {
  if (!health) {
    return (
      <EmptyState
        title="Backend unreachable"
        detail="Start Django (port 8000) and reload. The Vite dev server proxies /api to 127.0.0.1:8000."
      />
    );
  }

  const rows: [string, string | number | boolean][] = [
    ["API status", health.status],
    ["Database", health.database],
    ["SQLite journal", health.journal_mode],
    ["Gemini configured", health.gemini_configured ? "yes" : "no"],
    ["Jobs", health.total_jobs],
    ["Payments", health.total_payments],
    ["Gateway txs", health.total_gateway_transactions],
    ["Bank txs", health.total_bank_transactions],
    ["Reconciliations", health.total_reconciliations],
    ["Exceptions", health.total_exceptions],
    ["Audit logs", health.total_audit_logs],
  ];

  return (
    <div className="space-y-4 max-w-xl">
      <h3 className="text-xl font-black text-slate-900 tracking-tight">Settings</h3>
      <p className="text-sm text-slate-500">
        Live system health from <code className="font-mono text-xs">GET /api/health/</code>.
      </p>
      <div className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
        {rows.map(([k, v]) => (
          <div key={k} className="flex justify-between px-5 py-3 text-sm">
            <span className="text-slate-500">{k}</span>
            <span className="font-semibold text-slate-900 font-mono">{String(v)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
