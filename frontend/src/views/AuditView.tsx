import { useEffect, useMemo, useState } from "react";
import type React from "react";
import { Search, Terminal } from "lucide-react";
import type { AuditLog, ReconciliationResult } from "../types";
import { fetchTransactionAuditLogs, formatInr } from "../api/client";
import { EmptyState } from "../components/EmptyState";
import { StatusBadge } from "../components/StatusBadge";

interface AuditViewProps {
  results: ReconciliationResult[];
  selectedPaymentId: string | null;
  onSelectPayment: (id: string) => void;
}

export const AuditView: React.FC<AuditViewProps> = ({
  results,
  selectedPaymentId,
  onSelectPayment,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [logs, setLogs] = useState<AuditLog[]>([]);

  const filtered = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return results;
    return results.filter(
      (r) =>
        r.payment.toLowerCase().includes(q) ||
        (r.customer_name || "").toLowerCase().includes(q)
    );
  }, [results, searchQuery]);

  const currentId = selectedPaymentId || filtered[0]?.payment || null;

  useEffect(() => {
    if (!currentId) {
      queueMicrotask(() => setLogs([]));
      return;
    }
    fetchTransactionAuditLogs(currentId).then(setLogs).catch(() => setLogs([]));
  }, [currentId]);

  if (results.length === 0) {
    return (
      <EmptyState
        title="No audit history"
        detail="Run a reconciliation job to generate per-payment audit logs."
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-black text-slate-900 tracking-tight">Audit log</h3>
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search this page of results..."
            className="bg-white border border-slate-200 rounded-md pl-8 pr-3 py-1.5 text-xs w-64"
          />
        </div>
      </div>
      <div className="grid grid-cols-12 gap-6 items-start">
        <div className="col-span-4 bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="divide-y divide-slate-100 max-h-[720px] overflow-y-auto">
            {filtered.map((item) => (
              <button
                key={item.payment}
                onClick={() => onSelectPayment(item.payment)}
                className={`w-full text-left px-4 py-3 text-xs ${
                  item.payment === currentId ? "bg-slate-50 border-l-4 border-slate-900" : "hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono font-semibold">{item.payment}</span>
                  <StatusBadge status={item.status} />
                </div>
                <p className="text-slate-500 mt-1">
                  {item.customer_name} · {formatInr(item.payment_amount)}
                </p>
              </button>
            ))}
          </div>
        </div>
        <div className="col-span-8 bg-white border border-slate-200 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <Terminal className="w-4 h-4 text-slate-500" />
            <h4 className="font-bold text-sm">Trail for {currentId || "—"}</h4>
          </div>
          {logs.length === 0 ? (
            <p className="text-sm text-slate-500">No audit entries for this payment.</p>
          ) : (
            <div className="space-y-3 font-mono text-[11px]">
              {logs.map((log) => (
                <div key={log.id} className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                  <p className="text-slate-400">{log.created_at}</p>
                  <p>
                    <span className="text-emerald-700 font-bold">[{log.agent_node}]</span>{" "}
                    {log.tool_called || "no tool"}
                  </p>
                  {log.notes && <p className="text-slate-600 mt-1">{log.notes}</p>}
                  <pre className="mt-1.5 text-[10px] text-slate-600 overflow-x-auto bg-white p-2 rounded border border-slate-100">
                    {JSON.stringify({ input: log.tool_input, output: log.tool_output }, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
