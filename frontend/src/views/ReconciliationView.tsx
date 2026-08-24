import { useEffect, useState } from "react";
import type React from "react";
import { Search } from "lucide-react";
import type { ReconciliationResult } from "../types";
import { axiosErrorMessage, fetchJobResults, formatConfidence, formatInr } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import { EmptyState } from "../components/EmptyState";

interface ReconciliationViewProps {
  jobId: string | null;
  onSelectTransaction: (paymentId: string) => void;
}

const STATUSES = ["", "MATCHED", "MATCHED_DELAYED", "RESOLVED", "EXCEPTION", "UNRESOLVED"];

export const ReconciliationView: React.FC<ReconciliationViewProps> = ({
  jobId,
  onSelectTransaction,
}) => {
  const [results, setResults] = useState<ReconciliationResult[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const pageSize = 25;
  const totalPages = Math.max(1, Math.ceil(count / pageSize));

  useEffect(() => {
    if (!jobId) return;
    queueMicrotask(() => {
      setLoading(true);
      setError(null);
    });
    fetchJobResults(jobId, page, status || undefined, appliedSearch || undefined, pageSize)
      .then((data) => {
        setResults(data.results || []);
        setCount(data.count || 0);
      })
      .catch((err) => setError(axiosErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [jobId, page, status, appliedSearch]);

  if (!jobId) {
    return (
      <EmptyState
        title="No reconciliation job"
        detail="Generate a dataset and run reconciliation from + New Job."
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h3 className="text-xl font-black text-slate-900 tracking-tight">Batch processing</h3>
          <p className="text-xs text-slate-400 mt-0.5 font-mono">Job {jobId}</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  setPage(1);
                  setAppliedSearch(search);
                }
              }}
              placeholder="Search customer or payment ID"
              className="bg-white border border-slate-200 rounded-md pl-8 pr-3 py-1.5 text-xs w-56"
            />
          </div>
          <select
            value={status}
            onChange={(e) => {
              setPage(1);
              setStatus(e.target.value);
            }}
            className="border border-slate-200 bg-white text-xs font-semibold px-3 py-1.5 rounded"
          >
            <option value="">All statuses</option>
            {STATUSES.filter(Boolean).map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
          {error}
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
        {loading ? (
          <p className="text-sm text-slate-500 py-8 text-center">Loading results…</p>
        ) : results.length === 0 ? (
          <p className="text-sm text-slate-500 py-8 text-center">No results for this filter.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  <th className="pb-3">Payment ID</th>
                  <th className="pb-3">Customer</th>
                  <th className="pb-3 text-right">Amount</th>
                  <th className="pb-3 text-right">Difference</th>
                  <th className="pb-3 text-center">Status</th>
                  <th className="pb-3 text-right">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {results.map((item) => (
                  <tr
                    key={item.payment}
                    onClick={() => onSelectTransaction(item.payment)}
                    className="hover:bg-slate-50 cursor-pointer"
                  >
                    <td className="py-3 font-mono font-medium">{item.payment}</td>
                    <td className="py-3">{item.customer_name}</td>
                    <td className="py-3 text-right font-semibold">{formatInr(item.payment_amount)}</td>
                    <td className="py-3 text-right font-mono">{formatInr(item.difference)}</td>
                    <td className="py-3 text-center">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="py-3 text-right font-mono">{formatConfidence(item.confidence)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="flex items-center justify-between mt-4 text-xs text-slate-500">
          <span>
            {count} records · page {page} of {totalPages}
          </span>
          <div className="flex gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="border border-slate-200 px-3 py-1 rounded disabled:opacity-40"
            >
              Previous
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="border border-slate-200 px-3 py-1 rounded disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
