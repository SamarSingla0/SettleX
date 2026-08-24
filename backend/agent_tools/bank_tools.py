from typing import Dict, Any, List
from finance.models import BankTransaction


def find_bank_transaction(payment_id: str) -> Dict[str, Any]:
    """Searches bank statements matching reference or payment ID."""
    bank_txs = list(BankTransaction.objects.filter(reference__icontains=payment_id))
    if not bank_txs:
        return {"found": False, "count": 0, "transactions": []}

    records = [
        {
            "bank_transaction_id": b.bank_transaction_id,
            "reference": b.reference,
            "amount": str(b.amount),
            "transaction_date": str(b.transaction_date),
            "description": b.description or "",
            "bank_name": b.bank_name,
        }
        for b in bank_txs
    ]
    return {
        "found": True,
        "count": len(records),
        "transactions": records,
    }


def check_duplicate_transactions(payment_id: str) -> Dict[str, Any]:
    """Verifies whether multiple bank settlement credits were posted for the same payment."""
    bank_txs = list(BankTransaction.objects.filter(reference__icontains=payment_id))
    is_duplicate = len(bank_txs) > 1
    return {
        "is_duplicate": is_duplicate,
        "count": len(bank_txs),
        "transaction_ids": [b.bank_transaction_id for b in bank_txs],
        "evidence": f"Found {len(bank_txs)} bank entries matching reference '{payment_id}'." if is_duplicate else "No duplicate bank credits found.",
    }