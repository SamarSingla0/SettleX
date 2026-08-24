import { useEffect, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { DashboardView } from "./views/DashboardView";
import { ExceptionsView } from "./views/ExceptionsView";
import { EvaluationView } from "./views/EvaluationView";
import { ReconciliationView } from "./views/ReconciliationView";
import { AuditView } from "./views/AuditView";
import { SettingsView } from "./views/SettingsView";
import {
  fetchEvaluationOverview,
  fetchHealth,
  fetchJobDetail,
  fetchJobExceptions,
  fetchJobResults,
  generateDataset,
  runReconciliation,
} from "./api/client";
import type {
  EvaluationData,
  ExceptionRecord,
  ReconciliationJob,
  ReconciliationResult,
  SystemHealth,
} from "./types";

export function App() {
  const [currentTab, setCurrentTab] = useState<string>("dashboard");
  const [evalData, setEvalData] = useState<EvaluationData | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [job, setJob] = useState<ReconciliationJob | null>(null);
  const [results, setResults] = useState<ReconciliationResult[]>([]);
  const [exceptions, setExceptions] = useState<ExceptionRecord[]>([]);
  const [selectedPaymentId, setSelectedPaymentId] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setError(null);
      const [overview, systemHealth] = await Promise.all([
        fetchEvaluationOverview(),
        fetchHealth(),
      ]);
      setEvalData(overview);
      setHealth(systemHealth);
      if (overview.latest_job_id) {
        const [currentJob, res, jobExceptions] = await Promise.all([
          fetchJobDetail(overview.latest_job_id),
          fetchJobResults(overview.latest_job_id, 1),
          fetchJobExceptions(overview.latest_job_id, 1),
        ]);
        setJob(currentJob);
        setResults(res.results);
        setExceptions(jobExceptions.results);
      } else {
        setJob(null);
        setResults([]);
        setExceptions([]);
      }
    } catch (err) {
      console.error("Error loading reconciliation data:", err);
      setError("Could not load data from the backend. Ensure Django is running on port 8000.");
    }
  };

  useEffect(() => {
    void Promise.resolve().then(loadData);
  }, []);

  const handleRunAiCheck = async () => {
    setIsRunning(true);
    try {
      await runReconciliation(true);
      await loadData();
    } catch (err) {
      console.error("AI Check failed:", err);
      setError("The AI reconciliation run failed. Check the backend logs and configuration.");
    } finally {
      setIsRunning(false);
    }
  };

  const handleNewJob = async () => {
    setIsRunning(true);
    try {
      await generateDataset(150);
      await runReconciliation(true);
      await loadData();
    } catch (err) {
      console.error("New job generation failed:", err);
      setError("Could not generate and reconcile the new dataset.");
    } finally {
      setIsRunning(false);
    }
  };

  const handleExport = () => {
    if (results.length === 0) {
      setError("There are no reconciliation results available to export.");
      return;
    }

    const headings = ["Payment ID", "Customer", "Amount", "Currency", "Status", "Difference", "Confidence"];
    const rows = results.map((result) => [
      result.payment,
      result.customer_name,
      result.payment_amount,
      result.currency,
      result.status,
      result.difference,
      result.confidence,
    ]);
    const escapeCsv = (value: string | number) => `"${String(value).replaceAll('"', '""')}"`;
    const csv = [headings, ...rows].map((row) => row.map(escapeCsv).join(",")).join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `reconciliation-results-${job?.job_id?.slice(0, 8) ?? "latest"}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-[#f8f9fb] flex">
      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        onNewJob={handleNewJob}
      />

      {/* Main Content Area */}
      <div className="flex-1 ml-64 flex flex-col min-w-0">
        <Header
          currentTab={currentTab}
          setCurrentTab={setCurrentTab}
          onRunAiCheck={handleRunAiCheck}
          onExport={handleExport}
          isRunning={isRunning}
        />

        <main className="p-8 max-w-7xl w-full mx-auto">
          {error && (
            <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}
          {currentTab === "dashboard" && (
            <DashboardView
              evalData={evalData}
              job={job}
              recentResults={results}
              onSelectTransaction={(id) => {
                setSelectedPaymentId(id);
                setCurrentTab("exceptions");
              }}
              onViewAll={() => setCurrentTab("reconciliation")}
            />
          )}

          {currentTab === "exceptions" && (
            <ExceptionsView
              exceptions={exceptions}
              selectedPaymentId={selectedPaymentId}
              onSelectPayment={setSelectedPaymentId}
            />
          )}

          {currentTab === "evaluation" && (
            <EvaluationView evalData={evalData} exceptions={exceptions} />
          )}

          {currentTab === "reconciliation" && (
            <ReconciliationView
              jobId={job?.job_id ?? evalData?.latest_job_id ?? null}
              onSelectTransaction={(id) => {
                setSelectedPaymentId(id);
                setCurrentTab("audit");
              }}
            />
          )}

          {currentTab === "audit" && (
            <AuditView
              results={results}
              selectedPaymentId={selectedPaymentId}
              onSelectPayment={setSelectedPaymentId}
            />
          )}

          {currentTab === "settings" && <SettingsView health={health} />}
        </main>
      </div>
    </div>
  );
}

export default App;
