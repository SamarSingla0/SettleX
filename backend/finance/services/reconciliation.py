from decimal import Decimal
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.utils import timezone
from finance.models import (
    Payment,
    GatewayTransaction,
    BankTransaction,
    ReconciliationResult,
    ExceptionRecord,
    AuditLog,
    ReconciliationJob,
)
from reconciliation.graph import reconciliation_agent_graph


class DeterministicReconciliationEngine:
    """
    Pure Python & Django ORM reconciliation engine (No LLM).
    Used for baseline benchmarking and exact rule processing.
    """

    ALLOWED_SETTLEMENT_DELAY_DAYS = 3

    def __init__(self, job_id: Optional[str] = None):
        self.job = None
        if job_id:
            self.job = ReconciliationJob.objects.filter(job_id=job_id).first()

    @staticmethod
    def calculate_expected_settlement(payment: Payment, gateway_tx: Optional[GatewayTransaction]) -> Decimal:
        if not gateway_tx:
            return payment.amount
        total_fee = gateway_tx.gateway_fee + gateway_tx.tax_on_fee
        return payment.amount - total_fee

    def reconcile_payment(self, payment: Payment) -> Dict[str, Any]:
        evidence: List[str] = []

        gateway_tx = GatewayTransaction.objects.filter(payment=payment).first()
        if not gateway_tx:
            return {
                "payment": payment,
                "expected_amount": payment.amount,
                "actual_amount": None,
                "difference": payment.amount,
                "status": "UNRESOLVED",
                "confidence": 0.98,
                "reason": "Payment initiated but not captured by payment gateway.",
                "suggested_action": "Verify checkout logs and gateway webhook deliveries.",
                "evidence": ["No corresponding Gateway transaction found."],
                "exception_type": "MISSING_GATEWAY_RECORD",
            }

        expected_amount = self.calculate_expected_settlement(payment, gateway_tx)
        evidence.append(f"Expected Net: Rs {expected_amount}")

        bank_matches = list(BankTransaction.objects.filter(reference__icontains=payment.payment_id))
        if not bank_matches:
            bank_matches = list(BankTransaction.objects.filter(reference__icontains=gateway_tx.gateway_transaction_id))

        if len(bank_matches) > 1:
            total_credited = sum(b.amount for b in bank_matches)
            return {
                "payment": payment,
                "expected_amount": expected_amount,
                "actual_amount": total_credited,
                "difference": total_credited - expected_amount,
                "status": "EXCEPTION",
                "confidence": 0.99,
                "reason": f"Multiple bank transactions ({len(bank_matches)}) found for payment {payment.payment_id}.",
                "suggested_action": "Flag for finance operations audit to recover duplicate bank credit.",
                "evidence": [f"Found {len(bank_matches)} duplicate bank statement credits."],
                "exception_type": "DUPLICATE_SETTLEMENT",
            }

        if len(bank_matches) == 0:
            return {
                "payment": payment,
                "expected_amount": expected_amount,
                "actual_amount": None,
                "difference": expected_amount,
                "status": "UNRESOLVED",
                "confidence": 0.96,
                "reason": f"Gateway captured transaction, but no bank settlement credit found for {payment.payment_id}.",
                "suggested_action": "Contact bank operations / gateway settlement desk.",
                "evidence": ["No bank statement credit entry located."],
                "exception_type": "MISSING_BANK_TRANSACTION",
            }

        bank_tx = bank_matches[0]
        actual_amount = bank_tx.amount
        difference = abs(expected_amount - actual_amount)

        if difference != Decimal("0.00"):
            return {
                "payment": payment,
                "expected_amount": expected_amount,
                "actual_amount": actual_amount,
                "difference": difference,
                "status": "EXCEPTION",
                "confidence": 0.90,
                "reason": f"Discrepancy of Rs {difference} between expected net and bank credit.",
                "suggested_action": "Trigger AI agent investigation to analyze dispute fees.",
                "evidence": [f"Bank credited Rs {actual_amount}, expected Rs {expected_amount}."],
                "exception_type": "AMOUNT_MISMATCH",
            }

        settlement_delay = (bank_tx.transaction_date - payment.payment_date).days
        if settlement_delay > self.ALLOWED_SETTLEMENT_DELAY_DAYS:
            return {
                "payment": payment,
                "expected_amount": expected_amount,
                "actual_amount": actual_amount,
                "difference": Decimal("0.00"),
                "status": "MATCHED_DELAYED",
                "confidence": 0.98,
                "reason": f"Exact amount matched after delay of {settlement_delay} days.",
                "suggested_action": "No balance adjustment needed.",
                "evidence": [f"Settlement delay: {settlement_delay} days."],
                "exception_type": "DELAYED_SETTLEMENT",
                "is_resolved_delayed": True,
            }

        return {
            "payment": payment,
            "expected_amount": expected_amount,
            "actual_amount": actual_amount,
            "difference": Decimal("0.00"),
            "status": "MATCHED",
            "confidence": 0.99,
            "reason": "Exact deterministic match across Payment, Gateway, and Bank statement ledgers.",
            "suggested_action": "No action required.",
            "evidence": ["Exact ledger match confirmed."],
            "exception_type": None,
        }

    @transaction.atomic
    def run_batch(self) -> Dict[str, Any]:
        payments = list(Payment.objects.all())
        total = len(payments)

        if not self.job:
            self.job = ReconciliationJob.objects.create(total_records=total, status="PROCESSING")
        else:
            self.job.total_records = total
            self.job.status = "PROCESSING"
            self.job.save()

        ReconciliationResult.objects.all().delete()
        ExceptionRecord.objects.all().delete()
        AuditLog.objects.all().delete()

        results_to_create = []
        exceptions_to_create = []
        audit_logs_to_create = []

        matched_count = 0
        resolved_count = 0
        exception_count = 0
        unresolved_count = 0

        for payment in payments:
            decision = self.reconcile_payment(payment)

            result = ReconciliationResult(
                job=self.job,
                payment=payment,
                expected_amount=decision["expected_amount"],
                actual_amount=decision["actual_amount"],
                difference=decision["difference"],
                status=decision["status"],
                confidence=decision["confidence"],
                reason=decision["reason"],
                suggested_action=decision["suggested_action"],
                evidence=decision["evidence"],
                llm_response={},
            )
            results_to_create.append(result)

            if decision.get("exception_type"):
                exc = ExceptionRecord(
                    payment=payment,
                    exception_type=decision["exception_type"],
                    reason=decision["reason"],
                    suggested_action=decision["suggested_action"],
                    resolved=decision.get("is_resolved_delayed", False),
                )
                exceptions_to_create.append(exc)

            st = decision["status"]
            if st in ["MATCHED", "MATCHED_DELAYED"]:
                matched_count += 1
            elif st == "RESOLVED":
                resolved_count += 1
            elif st == "EXCEPTION":
                exception_count += 1
            elif st == "UNRESOLVED":
                unresolved_count += 1

        ReconciliationResult.objects.bulk_create(results_to_create)
        ExceptionRecord.objects.bulk_create(exceptions_to_create)

        match_rate = ((matched_count + resolved_count) / total) * 100 if total > 0 else 0.0
        self.job.matched_records = matched_count
        self.job.resolved_records = resolved_count
        self.job.exception_records = exception_count
        self.job.unresolved_records = unresolved_count
        self.job.match_rate = round(match_rate, 2)
        self.job.status = "COMPLETED"
        self.job.completed_at = timezone.now()
        self.job.save()

        return {
            "job_id": str(self.job.job_id),
            "total_records": total,
            "matched_records": matched_count,
            "resolved_records": resolved_count,
            "exception_records": exception_count,
            "unresolved_records": unresolved_count,
            "match_rate_pct": round(match_rate, 2),
        }


class FullReconciliationEngine:
    """
    Production reconciliation orchestrator combining deterministic rules
    with LangGraph multi-tool agent workflows.
    """

    def __init__(self, job_id: Optional[str] = None):
        self.job = None
        if job_id:
            self.job = ReconciliationJob.objects.filter(job_id=job_id).first()

    def process_payment(self, payment: Payment) -> Dict[str, Any]:
        initial_state = {
            "payment_id": payment.payment_id,
            "customer_name": payment.customer_name,
            "payment_amount": payment.amount,
            "currency": payment.currency,
            "payment_date": str(payment.payment_date),
            "gateway_found": False,
            "gateway_id": None,
            "gateway_fee": Decimal("0.00"),
            "tax_on_fee": Decimal("0.00"),
            "expected_amount": payment.amount,
            "gateway_status": "PENDING",
            "bank_found": False,
            "bank_transaction_count": 0,
            "actual_amount": None,
            "bank_description": None,
            "difference": Decimal("0.00"),
            "tool_evidence": [],
            "audit_trail": [],
            "needs_ai": False,
            "final_status": "EXCEPTION",
            "confidence": 0.0,
            "reason": "",
            "suggested_action": "",
            "fact_vs_hypothesis": "",
        }

        final_state = reconciliation_agent_graph.invoke(initial_state)
        return final_state

    @transaction.atomic
    def run_batch(self) -> Dict[str, Any]:
        payments = list(Payment.objects.all())
        total = len(payments)

        if not self.job:
            self.job = ReconciliationJob.objects.create(total_records=total, status="PROCESSING")
        else:
            self.job.total_records = total
            self.job.status = "PROCESSING"
            self.job.save()

        ReconciliationResult.objects.all().delete()
        ExceptionRecord.objects.all().delete()
        AuditLog.objects.all().delete()

        results_to_create = []
        exceptions_to_create = []
        audit_logs_to_create = []

        matched_count = 0
        resolved_count = 0
        exception_count = 0
        unresolved_count = 0

        for payment in payments:
            state = self.process_payment(payment)

            result = ReconciliationResult(
                job=self.job,
                payment=payment,
                expected_amount=state.get("expected_amount", payment.amount),
                actual_amount=state.get("actual_amount"),
                difference=state.get("difference", Decimal("0.00")),
                status=state.get("final_status", "EXCEPTION"),
                confidence=state.get("confidence", 0.0),
                reason=state.get("reason", ""),
                suggested_action=state.get("suggested_action", ""),
                evidence=state.get("tool_evidence", []),
                llm_response={
                    "status": state.get("final_status"),
                    "confidence": state.get("confidence"),
                    "fact_vs_hypothesis": state.get("fact_vs_hypothesis"),
                },
            )
            results_to_create.append(result)

            st = state.get("final_status")
            if st in ["EXCEPTION", "UNRESOLVED"]:
                exc = ExceptionRecord(
                    payment=payment,
                    exception_type="AMOUNT_MISMATCH" if state.get("difference", Decimal("0.00")) > 0 else "MISSING_RECORD",
                    reason=state.get("reason", "Exception requiring review"),
                    suggested_action=state.get("suggested_action", ""),
                    resolved=False,
                )
                exceptions_to_create.append(exc)

            for audit_step in state.get("audit_trail", []):
                audit = AuditLog(
                    payment=payment,
                    job_id=str(self.job.job_id),
                    agent_node=audit_step.get("node", "agent"),
                    tool_called=audit_step.get("tool"),
                    tool_output=audit_step.get("output", {}),
                    notes=state.get("reason", ""),
                )
                audit_logs_to_create.append(audit)

            if st in ["MATCHED", "MATCHED_DELAYED"]:
                matched_count += 1
            elif st == "RESOLVED":
                resolved_count += 1
            elif st == "EXCEPTION":
                exception_count += 1
            elif st == "UNRESOLVED":
                unresolved_count += 1

        ReconciliationResult.objects.bulk_create(results_to_create)
        ExceptionRecord.objects.bulk_create(exceptions_to_create)
        AuditLog.objects.bulk_create(audit_logs_to_create)

        match_rate = ((matched_count + resolved_count) / total) * 100 if total > 0 else 0.0
        self.job.matched_records = matched_count
        self.job.resolved_records = resolved_count
        self.job.exception_records = exception_count
        self.job.unresolved_records = unresolved_count
        self.job.match_rate = round(match_rate, 2)
        self.job.status = "COMPLETED"
        self.job.completed_at = timezone.now()
        self.job.save()

        return {
            "job_id": str(self.job.job_id),
            "total_records": total,
            "matched_records": matched_count,
            "resolved_records": resolved_count,
            "exception_records": exception_count,
            "unresolved_records": unresolved_count,
            "match_rate_pct": round(match_rate, 2),
        }