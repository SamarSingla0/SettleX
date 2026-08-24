import axios from "axios";
import type {
  AuditLog,
  EvaluationData,
  ExceptionRecord,
  PaginatedResponse,
  ReconciliationJob,
  ReconciliationResult,
  SystemHealth,
  TransactionDetail,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const fetchHealth = async (): Promise<SystemHealth> => {
  const { data } = await api.get<SystemHealth>("/health/");
  return data;
};

export const generateDataset = async (count: number = 150): Promise<unknown> => {
  const { data } = await api.post("/datasets/generate/", { count, seed: 42 });
  return data;
};

export const runReconciliation = async (useAi: boolean = true): Promise<unknown> => {
  const { data } = await api.post("/reconciliation/run/", { use_ai: useAi });
  return data;
};

export const fetchJobDetail = async (jobId: string): Promise<ReconciliationJob> => {
  const { data } = await api.get<ReconciliationJob>(`/reconciliation/${jobId}/`);
  return data;
};

export const fetchJobResults = async (
  jobId: string,
  page: number = 1,
  status?: string,
  search?: string,
  pageSize: number = 25
): Promise<PaginatedResponse<ReconciliationResult>> => {
  const params: Record<string, string | number> = { page, page_size: pageSize };
  if (status) params.status = status;
  if (search) params.search = search;
  const { data } = await api.get<PaginatedResponse<ReconciliationResult>>(
    `/reconciliation/${jobId}/results/`,
    { params }
  );
  return data;
};

export const fetchJobExceptions = async (
  jobId: string,
  page: number = 1,
  pageSize: number = 500
): Promise<PaginatedResponse<ExceptionRecord>> => {
  const { data } = await api.get<PaginatedResponse<ExceptionRecord>>(
    `/reconciliation/${jobId}/exceptions/`,
    { params: { page, page_size: pageSize } }
  );
  return data;
};

export const fetchEvaluationOverview = async (): Promise<EvaluationData> => {
  const { data } = await api.get<EvaluationData>("/evaluation/overview/");
  return data;
};

export const fetchTransactionDetail = async (
  paymentId: string
): Promise<TransactionDetail> => {
  const { data } = await api.get<TransactionDetail>(`/transactions/${paymentId}/`);
  return data;
};

export const fetchTransactionAuditLogs = async (
  paymentId: string
): Promise<AuditLog[]> => {
  const { data } = await api.get<AuditLog[]>(`/transactions/${paymentId}/audit/`);
  return data;
};

export function formatInr(value: string | number | null | undefined): string {
  const n = Number(value ?? 0);
  if (Number.isNaN(n)) return "—";
  return `₹${n.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function formatConfidence(confidence: number | null | undefined): string {
  const n = Number(confidence ?? 0);
  if (Number.isNaN(n)) return "0.0%";
  const pct = n <= 1 ? n * 100 : n;
  return `${pct.toFixed(1)}%`;
}

export function formatJobId(jobId: string | null | undefined): string {
  if (!jobId) return "No job";
  return jobId.slice(0, 8);
}

export function axiosErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data as { error?: string; detail?: string } | string | undefined;
    if (typeof detail === "string" && detail) return detail;
    if (detail && typeof detail === "object") {
      if (detail.error) return detail.error;
      if (detail.detail) return String(detail.detail);
    }
    if (err.code === "ERR_NETWORK") {
      return "Cannot reach the backend. Start Django on port 8000.";
    }
    return err.message;
  }
  return "Unexpected error";
}
