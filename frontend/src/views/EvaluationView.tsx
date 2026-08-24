import { useMemo } from "react";
import type React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EvaluationData, ExceptionRecord } from "../types";
import { formatConfidence } from "../api/client";
import { EmptyState } from "../components/EmptyState";
import { StatusBadge } from "../components/StatusBadge";

interface EvaluationViewProps {
  evalData: EvaluationData | null;
  exceptions: ExceptionRecord[];
}

export const EvaluationView: React.FC<EvaluationViewProps> = ({ evalData, exceptions }) => {
  const gt = evalData?.ground_truth_evaluation;
  const metrics = evalData?.metrics;
  const total = metrics?.total_records ?? gt?.total_records;
  const accuracy = metrics?.accuracy_pct ?? gt?.accuracy_pct;
  const precision = metrics?.precision_pct ?? gt?.precision_pct;
  const recall = metrics?.recall_pct ?? gt?.recall_pct;
  const breakdown = metrics?.breakdown ?? gt?.breakdown;

  const donutData = useMemo(
    () => [
      { name: "Matched", value: breakdown?.matched ?? 0, color: "#047857" },
      { name: "Resolved", value: breakdown?.resolved ?? 0, color: "#2dd4bf" },
      { name: "Exception", value: breakdown?.exceptions ?? 0, color: "#dc2626" },
      { name: "Unresolved", value: breakdown?.unresolved ?? 0, color: "#94a3b8" },
    ],
    [breakdown]
  );

  const confusionData = useMemo(
    () => [
      { label: "True positives", count: metrics?.true_positives ?? gt?.true_positives ?? 0 },
      { label: "False positives", count: metrics?.false_positives ?? gt?.false_positives ?? 0 },
      { label: "False negatives", count: metrics?.false_negatives ?? gt?.false_negatives ?? 0 },
      { label: "True negatives", count: metrics?.true_negatives ?? gt?.true_negatives ?? 0 },
    ],
    [metrics, gt]
  );

  const categoryData = useMemo(() => {
    const counts = new Map<string, number>();
    for (const ex of exceptions) {
      counts.set(ex.exception_type, (counts.get(ex.exception_type) ?? 0) + 1);
    }
    return Array.from(counts.entries()).map(([category, count]) => ({
      category: category.replaceAll("_", " "),
      count,
    }));
  }, [exceptions]);

  const discrepancies = gt?.discrepancies ?? [];

  if (!evalData) {
    return (
      <EmptyState
        title="No evaluation yet"
        detail="Run a reconciliation job to compute accuracy against ground truth."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-black text-slate-900 tracking-tight">System evaluation</h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Live metrics for job {evalData.latest_job_id ?? "—"} compared with ground truth.
        </p>
      </div>

      <div className="grid grid-cols-4 gap-5">
        <MetricCard label="Dataset size" value={total ?? "—"} />
        <MetricCard label="Accuracy" value={fmtPct(accuracy)} />
        <MetricCard label="Precision" value={fmtPct(precision)} />
        <MetricCard label="Recall" value={fmtPct(recall)} />
      </div>

      <div className="grid grid-cols-12 gap-5">
        <div className="col-span-5 bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
          <h4 className="font-bold text-slate-900 text-sm mb-4">Status distribution</h4>
          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={donutData}
                  innerRadius={65}
                  outerRadius={95}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {donutData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-4 text-xs">
            {donutData.map((d) => (
              <div key={d.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: d.color }} />
                <span className="text-slate-600 font-medium">
                  {d.name}: <strong className="text-slate-900">{d.value}</strong>
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="col-span-7 bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
          <h4 className="font-bold text-slate-900 text-sm mb-4">
            Classification vs ground truth
          </h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={confusionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="label" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#0f172a" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-5">
        <div className="col-span-4 bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
          <h4 className="font-bold text-slate-900 text-sm mb-4">Exception categories</h4>
          {categoryData.length === 0 ? (
            <p className="text-sm text-slate-500">No exception records to chart.</p>
          ) : (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#f8fafc" />
                  <XAxis type="number" stroke="#94a3b8" fontSize={11} allowDecimals={false} />
                  <YAxis
                    type="category"
                    dataKey="category"
                    stroke="#94a3b8"
                    fontSize={10}
                    width={110}
                  />
                  <Tooltip />
                  <Bar dataKey="count" fill="#475569" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="col-span-8 bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-bold text-slate-900 text-sm">Edge case analysis</h4>
            <span className="text-xs text-slate-400 font-medium">
              Ground truth vs system decision
            </span>
          </div>
          {discrepancies.length === 0 ? (
            <p className="text-sm text-slate-500">No classification discrepancies in this batch.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    <th className="pb-2">Txn ID</th>
                    <th className="pb-2">Scenario</th>
                    <th className="pb-2 text-center">Ground truth</th>
                    <th className="pb-2 text-center">AI decision</th>
                    <th className="pb-2 text-right">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {discrepancies.map((row) => (
                    <tr key={row.payment_id} className="hover:bg-slate-50/50">
                      <td className="py-2.5 font-mono text-slate-900">{row.payment_id}</td>
                      <td className="py-2.5 text-slate-600">{row.scenario}</td>
                      <td className="py-2.5 text-center">
                        <StatusBadge status={row.expected_status} />
                      </td>
                      <td className="py-2.5 text-center">
                        <StatusBadge status={row.actual_status} />
                      </td>
                      <td className="py-2.5 text-right font-mono font-bold text-slate-900">
                        {formatConfidence(row.confidence)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function fmtPct(n: number | undefined): string {
  return n == null ? "—" : `${n}%`;
}

const MetricCard: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
  <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
    <p className="text-[11px] font-bold tracking-wider text-slate-400 uppercase">{label}</p>
    <h3 className="text-3xl font-extrabold text-slate-900 mt-2">{value}</h3>
  </div>
);
