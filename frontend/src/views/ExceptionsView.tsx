import { useEffect, useMemo, useState } from "react";
import type React from "react";
import {
  ArrowUpDown,
  Bot,
  CheckCircle2,
  Filter,
  Search,
  Terminal,
  XCircle,
} from "lucide-react";
import type { AuditLog, ExceptionRecord, TransactionDetail } from "../types";
import {
  fetchTransactionAuditLogs,
  fetchTransactionDetail,
  formatConfidence,
  formatInr,
} from "../api/client";
import { EmptyState } from "../components/EmptyState";
import { StatusBadge } from "../components/StatusBadge";

interface ExceptionsViewProps {
  exceptions: ExceptionRecord[];
  selectedPaymentId: string | null;
  onSelectPayment: (id: string) => void;
}

export const ExceptionsView: React.FC<ExceptionsViewProps> = ({
  exceptions,
  selectedPaymentId,
  onSelectPayment,
}) => {
  const [detail, setDetail] = useState<TransactionDetail | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("ALL");
  const [sortDir, setSortDir] = useState<"desc" | "asc">("desc");
  const [detailError, setDetailError] = useState<string | null>(null);

  const types = useMemo(
    () => Array.from(new Set(exceptions.map((e) => e.exception_type))).sort(),
    [exceptions]
  );

  const filtered = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return exceptions
      .filter((r) => {
        if (typeFilter !== "ALL" && r.exception_type !== typeFilter) return false;
        if (!q) return true;
        return (
          r.payment.toLowerCase().includes(q) ||
          (r.customer_name || "").toLowerCase().includes(q) ||
          (r.reason || "").toLowerCase().includes(q) ||
          (r.exception_type || "").toLowerCase().includes(q)
        );
      })
      .sort((a, b) => {
        const da = Number(a.payment_amount);
        const db = Number(b.payment_amount);
        return sortDir === "desc" ? db - da : da - db;
      });
  }, [exceptions, searchQuery, typeFilter, sortDir]);

  const currentId = selectedPaymentId || filtered[0]?.payment || null;

  useEffect(() => {
    if (!currentId) {
      queueMicrotask(() => {
        setDetail(null);
        setAuditLogs([]);
      });
      return;
    }
    queueMicrotask(() => setDetailError(null));
    fetchTransactionDetail(currentId)
      .then(setDetail)
      .catch(() => {
        setDetail(null);
        setDetailError(`Could not load payment ${currentId}.`);
      });
    fetchTransactionAuditLogs(currentId).then(setAuditLogs).catch(() => setAuditLogs([]));
  }, [currentId]);

  if (exceptions.length === 0) {
    return (
      <EmptyState
        title="No exceptions"
        detail="Run a reconciliation job to populate exception records."
      />
    );
  }

  const rec = detail?.reconciliation_result;
  const diff = Number(rec?.difference ?? 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h3 className="text-xl font-black text-slate-900 tracking-tight">
          Unresolved exceptions
        </h3>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search payment, customer, reason..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-white border border-slate-200 rounded-md pl-8 pr-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-400 w-64"
            />
          </div>
          <div className="relative">
            <Filter className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="border border-slate-200 bg-white text-slate-700 text-xs font-semibold pl-8 pr-3 py-1.5 rounded appearance-none"
            >
              <option value="ALL">All types</option>
              {types.map((t) => (
                <option key={t} value={t}>
                  {t.replaceAll("_", " ")}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={() => setSortDir((d) => (d === "desc" ? "asc" : "desc"))}
            className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded flex items-center gap-1.5"
          >
            <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
            Amount {sortDir === "desc" ? "↓" : "↑"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6 items-start">
        <div className="col-span-4 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs">
          <div className="grid grid-cols-12 text-[11px] font-bold text-slate-400 uppercase tracking-wider px-4 py-3 border-b border-slate-100 bg-slate-50/50">
            <div className="col-span-3">Txn ID</div>
            <div className="col-span-5">Type</div>
            <div className="col-span-4 text-right">Amount</div>
          </div>
          <div className="divide-y divide-slate-100 max-h-[700px] overflow-y-auto">
            {filtered.length === 0 && (
              <p className="text-xs text-slate-500 p-4">No exceptions match this search.</p>
            )}
            {filtered.map((item) => {
              const isSelected = item.payment === currentId;
              return (
                <div
                  key={`${item.id}-${item.payment}`}
                  onClick={() => onSelectPayment(item.payment)}
                  className={`grid grid-cols-12 items-center px-4 py-3 cursor-pointer text-xs transition-colors ${
                    isSelected
                      ? "bg-slate-50 border-l-4 border-slate-900 font-semibold"
                      : "hover:bg-slate-50/50"
                  }`}
                >
                  <div className="col-span-3 font-mono text-slate-900">{item.payment}</div>
                  <div className="col-span-5 text-slate-500 truncate" title={item.exception_type}>
                    {item.exception_type.replaceAll("_", " ")}
                  </div>
                  <div className="col-span-4 text-right">
                    <p className="text-slate-900 font-semibold">{formatInr(item.payment_amount)}</p>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        item.resolved ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
                      }`}
                    >
                      {item.resolved ? "Resolved" : "Open"}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="col-span-8 space-y-5">
          {detailError && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
              {detailError}
            </div>
          )}
          {detail && (
            <>
              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs font-mono font-medium text-slate-400">
                      Transaction {detail.payment.payment_id}
                    </span>
                    <h2 className="text-2xl font-black text-slate-900 tracking-tight mt-1">
                      {detail.payment.customer_name}
                    </h2>
                    <div className="flex items-center gap-6 mt-3 text-xs">
                      <div>
                        <span className="text-slate-400 block text-[11px]">Payment amount</span>
                        <span className="font-extrabold text-slate-900 text-base">
                          {formatInr(detail.payment.amount)}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[11px]">Payment date</span>
                        <span className="font-semibold text-slate-700">
                          {detail.payment.payment_date}
                        </span>
                      </div>
                    </div>
                  </div>
                  <StatusBadge status={rec?.status || "UNRESOLVED"} />
                </div>

                <div className="grid grid-cols-4 gap-4 mt-6">
                  <Fact label="Gateway fee" value={formatInr(detail.gateway_transaction?.gateway_fee)} />
                  <Fact label="Expected settlement" value={formatInr(rec?.expected_amount)} />
                  <Fact
                    label="Actual settlement"
                    value={rec?.actual_amount != null ? formatInr(rec.actual_amount) : "—"}
                  />
                  <div className="bg-red-50/50 border border-red-200/70 rounded-lg p-3.5">
                    <p className="text-[11px] font-semibold text-red-600">Difference</p>
                    <p className="text-lg font-black text-red-600 mt-1">{formatInr(rec?.difference)}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
                <div className="flex items-center gap-2">
                  <Bot className="w-5 h-5 text-emerald-700" />
                  <h4 className="font-bold text-slate-900 text-sm">AI investigation summary</h4>
                </div>
                <div className="space-y-2 text-xs">
                  {(rec?.evidence || []).map((ev: string, idx: number) => (
                    <div key={idx} className="flex items-center gap-2 text-slate-700">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>{ev}</span>
                    </div>
                  ))}
                  {diff !== 0 && (
                    <div className="flex items-center gap-2 text-red-600 bg-red-50 p-2 rounded-md font-medium">
                      <XCircle className="w-4 h-4 text-red-600 shrink-0" />
                      <span>Difference of {formatInr(rec?.difference)} remains.</span>
                    </div>
                  )}
                  {(rec?.evidence || []).length === 0 && diff === 0 && (
                    <p className="text-slate-500">No evidence recorded for this payment.</p>
                  )}
                </div>
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mt-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                      AI conclusion
                    </span>
                    <span className="bg-emerald-100 text-emerald-800 text-[11px] font-bold px-2 py-0.5 rounded">
                      Conf: {formatConfidence(rec?.confidence)}
                    </span>
                  </div>
                  <p className="text-xs font-semibold text-slate-900 leading-relaxed">
                    <span className="text-red-600 font-bold uppercase">{rec?.status}.</span>{" "}
                    {rec?.reason}
                  </p>
                  <p className="text-[11px] text-slate-500 mt-2 font-medium">
                    Recommended action: {rec?.suggested_action || "—"}
                  </p>
                </div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
                <div className="flex items-center gap-2 mb-4">
                  <Terminal className="w-4 h-4 text-slate-500" />
                  <h4 className="font-bold text-slate-900 text-sm">Audit trail</h4>
                </div>
                {auditLogs.length === 0 ? (
                  <p className="text-xs text-slate-500">No audit logs for this payment.</p>
                ) : (
                  <div className="space-y-3 font-mono text-[11px]">
                    {auditLogs.map((log) => (
                      <div
                        key={log.id}
                        className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-slate-800"
                      >
                        <span className="text-emerald-700 font-bold">[{log.agent_node}]</span> CALL{" "}
                        <span className="font-bold">{log.tool_called || "none"}()</span>
                        <pre className="mt-1.5 text-[10px] text-slate-600 overflow-x-auto bg-white p-2 rounded border border-slate-100">
                          {JSON.stringify(log.tool_output, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

const Fact: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="bg-slate-50 border border-slate-200/70 rounded-lg p-3.5">
    <p className="text-[11px] font-semibold text-slate-500">{label}</p>
    <p className="text-lg font-bold text-slate-900 mt-1">{value}</p>
  </div>
);
