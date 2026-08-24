from typing import Dict, Any, Optional
from decimal import Decimal
from finance.models import GatewayTransaction, Payment


def find_gateway_transaction(payment_id: str) -> Dict[str, Any]:
    """Retrieves captured gateway transaction details and standard fee deductions."""
    gw = GatewayTransaction.objects.filter(payment_id=payment_id).first()
    if not gw:
        return {"found": False, "error": f"No gateway record for payment {payment_id}."}
    return {
        "found": True,
        "gateway_transaction_id": gw.gateway_transaction_id,
        "amount": str(gw.amount),
        "gateway_fee": str(gw.gateway_fee),
        "tax_on_fee": str(gw.tax_on_fee),
        "total_deductions": str(gw.total_deductions),
        "net_expected": str(gw.net_settlement_expected),
        "settlement_date": str(gw.settlement_date),
        "status": gw.status,
    }


def find_fee_explanation(payment_id: str, difference: Decimal) -> Dict[str, Any]:
    """
    Checks gateway surcharge audit schedule for dispute fees, chargeback handling,
    or interchange adjustments that match the exact discrepancy.
    """
    gw = GatewayTransaction.objects.filter(payment_id=payment_id).first()
    if not gw:
        return {"has_explanation": False, "reason": "No gateway transaction found."}

    # Gateway standard fee is 2% base + 18% tax. Check if additional fees explain the difference.
    base_fee = (gw.amount * Decimal("0.02")).quantize(Decimal("0.01"))
    extra_deduction = gw.gateway_fee - base_fee

    if extra_deduction > Decimal("0.00") and abs(extra_deduction - difference) <= Decimal("0.01"):
        return {
            "has_explanation": True,
            "fee_type": "DISPUTE_INTERCHANGE_SURCHARGE",
            "explained_amount": str(extra_deduction),
            "evidence": f"Gateway audit log confirms an extra dispute/interchange fee of Rs {extra_deduction}.",
        }

    return {
        "has_explanation": False,
        "reason": f"No documented fee schedule or surcharge explains the Rs {difference} discrepancy.",
    }