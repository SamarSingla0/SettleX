import type React from "react";
import { ArrowUpRight } from "lucide-react";
import type { EvaluationData, ReconciliationJob, ReconciliationResult } from "../types";
import { formatConfidence, formatInr, formatJobId } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import { EmptyState } from "../components/EmptyState";

interface DashboardViewProps {
  evalData: EvaluationData | null;
  job: ReconciliationJob | null;
  recentResults: ReconciliationResult[];
  onSelectTransaction: (paymentId: string) => void;
  onViewAll: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  evalData,
  job,
  recentResults,
  onSelectTransaction,
  onViewAll,
}) => {
  const metrics = evalData?.metrics;
  const gt = evalData?.ground_truth_evaluation;
  const breakdown = job
    ? {
        matched: job.matched_records,
        resolved: job.resolved_records,
        exceptions: job.exception_records,
        unresolved: job.unresolved_records,
      }
    : metrics?.breakdown ?? gt?.breakdown;

  const total =
    job?.total_records ?? metrics?.total_records ?? gt?.total_records ?? 0;
  const matchedCount = (breakdown?.matched ?? 0) + (breakdown?.resolved ?? 0);
  const accuracy = job?.accuracy ?? metrics?.accuracy_pct ?? gt?.accuracy_pct;
  const matchRate = job?.match_rate ?? metrics?.match_rate_pct ?? gt?.match_rate_pct;
  const processed = matchedCount + (breakdown?.exceptions ?? 0) + (breakdown?.unresolved ?? 0);
  const progressPct =
    job?.status === "COMPLETED"
      ? 100
      : total > 0
        ? Math.round((processed / total) * 100)
        : 0;

  if (!evalData && !job) {
    return (
      <EmptyState
        title="No reconciliation data yet"
        detail="Click + New Job to generate a dataset and run reconciliation, or Run AI Check if data already exists."
      />
    );
  }

  const matchedPct = total > 0 ? Math.round((matchedCount / total) * 100) : 0;
  const exceptionPct =
    total > 0 ? Math.round(((breakdown?.exceptions ?? 0) / total) * 100) : 0;
  const unresolvedPct =
    total > 0 ? Math.round(((breakdown?.unresolved ?? 0) / total) * 100) : 0;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-5">
        <Kpi label="Total transactions" value={total} />
        <Kpi
          label="Matched"
          value={matchedCount}
          badge={`${matchedPct}%`}
          badgeClass="bg-emerald-50 text-emerald-700"
        />
        <Kpi
          label="Exceptions"
          value={breakdown?.exceptions ?? 0}
          badge={`${exceptionPct}%`}
          badgeClass="bg-red-50 text-red-600"
        />
        <Kpi
          label="Unresolved"
          value={breakdown?.unresolved ?? 0}
          badge={`${unresolvedPct}%`}
          badgeClass="bg-slate-100 text-slate-600"
        />
      </div>

      <div className="grid grid-cols-12 gap-5">
        <div className="col-span-5 space-y-4">
          <MeterCard label="Match rate" value={matchRate} barClass="bg-emerald-700" />
          <MeterCard label="System accuracy" value={accuracy} barClass="bg-black" />
        </div>

        <div className="col-span-7 bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <h4 className="text-lg font-bold text-slate-900">Current reconciliation job</h4>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Job ID: {formatJobId(job?.job_id ?? evalData?.latest_job_id)}{" "}
              {job?.status ? `· ${job.status}` : ""}
            </p>
          </div>
          <div className="my-6">
            <h2 className="text-4xl font-black text-slate-900 mb-4">{progressPct}%</h2>
            <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
              <div
                className="bg-emerald-700 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(progressPct, 100)}%` }}
              />
            </div>
            <p className="text-right text-xs font-bold text-slate-500 mt-2">
              {processed}/{total} processed
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <h4 className="font-bold text-slate-900 text-base">Recent activity</h4>
          <button
            onClick={onViewAll}
            className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1"
          >
            View all <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
        {recentResults.length === 0 ? (
          <p className="text-sm text-slate-500 py-6 text-center">No results for this job yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  <th className="pb-3">Payment ID</th>
                  <th className="pb-3">Customer</th>
                  <th className="pb-3 text-right">Amount</th>
                  <th className="pb-3 text-center">Status</th>
                  <th className="pb-3 text-right">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {recentResults.slice(0, 8).map((item) => (
                  <tr
                    key={item.payment}
                    onClick={() => onSelectTransaction(item.payment)}
                    className="hover:bg-slate-50 cursor-pointer transition-colors"
                  >
                    <td className="py-3 font-mono font-medium text-slate-900">{item.payment}</td>
                    <td className="py-3 font-medium text-slate-700">{item.customer_name}</td>
                    <td className="py-3 text-right font-semibold text-slate-900">
                      {formatInr(item.payment_amount)}
                    </td>
                    <td className="py-3 text-center">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="py-3 text-right font-mono font-semibold">
                      <span className={item.confidence >= 0.9 ? "text-slate-900" : "text-red-600"}>
                        {formatConfidence(item.confidence)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

const Kpi: React.FC<{
  label: string;
  value: number;
  badge?: string;
  badgeClass?: string;
}> = ({ label, value, badge, badgeClass }) => (
  <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
    <p className="text-[11px] font-bold tracking-wider text-slate-400 uppercase">{label}</p>
    <div className="flex items-baseline gap-3 mt-2">
      <h3 className="text-3xl font-extrabold text-slate-900">{value}</h3>
      {badge && (
        <span className={`${badgeClass} text-xs font-bold px-2 py-0.5 rounded`}>{badge}</span>
      )}
    </div>
  </div>
);

const MeterCard: React.FC<{
  label: string;
  value: number | undefined;
  barClass: string;
}> = ({ label, value, barClass }) => {
  const pct = value ?? 0;
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
      <p className="text-[11px] font-bold tracking-wider text-slate-400 uppercase">{label}</p>
      <h4 className="text-2xl font-black text-slate-900 mt-1 mb-3">
        {value == null ? "—" : `${pct}%`}
      </h4>
      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
        <div
          className={`${barClass} h-full rounded-full transition-all duration-500`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
    </div>
  );
};
