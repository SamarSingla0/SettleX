from typing import Dict, Any, Optional
from decimal import Decimal
from finance.models import Payment


def find_payment(payment_id: str) -> Dict[str, Any]:
    """Retrieves payment metadata and customer details."""
    payment = Payment.objects.filter(payment_id=payment_id).first()
    if not payment:
        return {"found": False, "error": f"Payment {payment_id} not found."}
    return {
        "found": True,
        "payment_id": payment.payment_id,
        "customer_name": payment.customer_name,
        "amount": str(payment.amount),
        "currency": payment.currency,
        "payment_date": str(payment.payment_date),
        "gateway": payment.gateway,
    }