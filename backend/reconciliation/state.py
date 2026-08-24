from typing import TypedDict, List, Dict, Any, Optional
from decimal import Decimal


class ReconciliationState(TypedDict):
    # Core identifiers
    payment_id: str
    customer_name: str
    payment_amount: Decimal
    currency: str
    payment_date: str

    # Gateway Ledger
    gateway_found: bool
    gateway_id: Optional[str]
    gateway_fee: Decimal
    tax_on_fee: Decimal
    expected_amount: Decimal
    gateway_status: str

    # Bank Ledger
    bank_found: bool
    bank_transaction_count: int
    actual_amount: Optional[Decimal]
    bank_description: Optional[str]
    difference: Decimal

    # Investigation & Evidence
    tool_evidence: List[str]
    audit_trail: List[Dict[str, Any]]
    needs_ai: bool

    # Final Verdict
    final_status: str
    confidence: float
    reason: str
    suggested_action: str
    fact_vs_hypothesis: str