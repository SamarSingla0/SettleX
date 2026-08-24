export type TransactionStatus =
  | "MATCHED"
  | "MATCHED_DELAYED"
  | "RESOLVED"
  | "EXCEPTION"
  | "UNRESOLVED";

export interface SystemHealth {
  status: string;
  database: string;
  journal_mode: string;
  gemini_configured: boolean;
  total_jobs: number;
  total_payments: number;
  total_gateway_transactions: number;
  total_bank_transactions: number;
  total_reconciliations: number;
  total_exceptions: number;
  total_audit_logs: number;
}

export interface ReconciliationJob {
  job_id: string;
  total_records: number;
  matched_records: number;
  resolved_records: number;
  exception_records: number;
  unresolved_records: number;
  match_rate: number;
  accuracy: number;
  avg_confidence: number;
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  error_message?: string | null;
  started_at: string;
  completed_at?: string | null;
}

export interface ReconciliationResult {
  payment: string;
  customer_name: string;
  currency: string;
  payment_amount: string;
  payment_date: string;
  gateway: string;
  expected_amount: string;
  actual_amount: string | null;
  difference: string;
  status: TransactionStatus;
  confidence: number;
  reason: string;
  suggested_action: string;
  evidence: string[];
  llm_response: {
    status?: string;
    confidence?: number;
    fact_vs_hypothesis?: string;
  };
  created_at: string;
}

export interface ExceptionRecord {
  id: number;
  payment: string;
  customer_name: string;
  payment_amount: string;
  exception_type: string;
  reason: string;
  suggested_action: string;
  resolved: boolean;
  created_at: string;
}

export interface AuditLog {
  id: number;
  payment: string | null;
  job_id: string | null;
  agent_node: string;
  tool_called: string | null;
  tool_input: Record<string, unknown>;
  tool_output: Record<string, unknown>;
  llm_response: Record<string, unknown>;
  notes: string | null;
  created_at: string;
}

export interface Payment {
  payment_id: string;
  customer_name: string;
  amount: string;
  currency: string;
  payment_date: string;
  gateway: string;
}

export interface GatewayTransaction {
  gateway_transaction_id: string;
  payment: string | null;
  amount: string;
  gateway_fee: string;
  tax_on_fee: string;
  settlement_date: string | null;
  status: string;
  total_deductions?: string;
  net_settlement_expected?: string;
}

export interface BankTransaction {
  bank_transaction_id: string;
  reference: string;
  amount: string;
  transaction_date: string;
  description: string | null;
  bank_name: string;
}

export interface GroundTruthRecord {
  payment_id: string;
  customer_name: string;
  scenario_type: string;
  expected_status: string;
  expected_confidence: number;
  expected_difference: string;
  expected_reason: string;
  is_resolvable: boolean;
}

export interface StatusBreakdown {
  matched: number;
  resolved: number;
  exceptions: number;
  unresolved: number;
}

export interface JobMetrics {
  job_id?: string;
  total_records?: number;
  accuracy_pct?: number;
  match_rate_pct?: number;
  precision_pct?: number;
  recall_pct?: number;
  avg_confidence_pct?: number;
  true_positives?: number;
  false_positives?: number;
  false_negatives?: number;
  true_negatives?: number;
  breakdown?: StatusBreakdown;
  error?: string;
}

export interface GroundTruthEvaluation {
  total_records: number;
  evaluated_records: number;
  accuracy_pct: number;
  match_rate_pct: number;
  precision_pct: number;
  recall_pct: number;
  avg_confidence_pct: number;
  true_positives?: number;
  false_positives?: number;
  false_negatives?: number;
  true_negatives?: number;
  breakdown: StatusBreakdown;
  discrepancies: Array<{
    payment_id: string;
    expected_status: string;
    actual_status: string;
    scenario: string;
    confidence: number;
    reason: string;
  }>;
  discrepancies_count?: number;
  error?: string;
}

export interface EvaluationData {
  latest_job_id: string | null;
  metrics: JobMetrics;
  ground_truth_evaluation: GroundTruthEvaluation;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface TransactionDetail {
  payment: Payment;
  gateway_transaction: GatewayTransaction | null;
  bank_transactions: BankTransaction[];
  reconciliation_result: ReconciliationResult | null;
  exceptions: ExceptionRecord[];
  ground_truth: GroundTruthRecord | null;
}
