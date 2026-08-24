from decimal import Decimal
from typing import Dict, Any
from reconciliation.state import ReconciliationState
from agent_tools.payment_tools import find_payment
from agent_tools.gateway_tools import find_gateway_transaction, find_fee_explanation
from agent_tools.bank_tools import find_bank_transaction, check_duplicate_transactions
from agent_tools.entity_tools import match_customer_entity
from finance.services.gemini_client import GeminiInvestigationClient


def load_and_match_ledgers_node(state: ReconciliationState) -> Dict[str, Any]:
    """Node 1: Loads ledgers, calculates expected settlement, and verifies bank credit."""
    pid = state["payment_id"]
    evidence = list(state.get("tool_evidence", []))
    audit = list(state.get("audit_trail", []))

    # 1. Lookup Payment
    pay_res = find_payment(pid)
    audit.append({"node": "load_and_match", "tool": "find_payment", "output": pay_res})
    if not pay_res["found"]:
        return {
            "needs_ai": False,
            "final_status": "UNRESOLVED",
            "confidence": 0.99,
            "reason": f"Payment {pid} not found in database.",
            "suggested_action": "Check billing system sync.",
            "tool_evidence": ["Payment record missing."],
            "audit_trail": audit,
        }

    evidence.append(f"Payment {pid} registered for {pay_res['customer_name']} (Rs {pay_res['amount']}).")

    # 2. Lookup Gateway
    gw_res = find_gateway_transaction(pid)
    audit.append({"node": "load_and_match", "tool": "find_gateway_transaction", "output": gw_res})
    if not gw_res["found"]:
        evidence.append("Gateway transaction missing.")
        return {
            "gateway_found": False,
            "needs_ai": False,
            "final_status": "UNRESOLVED",
            "confidence": 0.98,
            "reason": "Payment initiated but no gateway capture record exists.",
            "suggested_action": "Verify gateway webhook logs.",
            "tool_evidence": evidence,
            "audit_trail": audit,
        }

    expected_net = Decimal(gw_res["net_expected"])
    evidence.append(f"Gateway captured transaction. Expected net settlement: Rs {expected_net}.")

    # 3. Lookup Bank Transactions
    bank_res = find_bank_transaction(pid)
    audit.append({"node": "load_and_match", "tool": "find_bank_transaction", "output": bank_res})

    if not bank_res["found"]:
        evidence.append("No bank transaction found with payment reference.")
        return {
            "gateway_found": True,
            "bank_found": False,
            "expected_amount": expected_net,
            "actual_amount": None,
            "difference": expected_net,
            "needs_ai": False,
            "final_status": "UNRESOLVED",
            "confidence": 0.96,
            "reason": "Gateway captured transaction, but no bank settlement credit was found.",
            "suggested_action": "Escalate to bank operations desk with gateway transaction UTR.",
            "tool_evidence": evidence,
            "audit_trail": audit,
        }

    # 4. Check Duplicates
    dup_res = check_duplicate_transactions(pid)
    audit.append({"node": "load_and_match", "tool": "check_duplicate_transactions", "output": dup_res})
    if dup_res["is_duplicate"]:
        total_credited = sum(Decimal(tx["amount"]) for tx in bank_res["transactions"])
        evidence.append(f"Duplicate settlement detected: {dup_res['count']} bank credits found.")
        return {
            "gateway_found": True,
            "bank_found": True,
            "bank_transaction_count": dup_res["count"],
            "expected_amount": expected_net,
            "actual_amount": total_credited,
            "difference": total_credited - expected_net,
            "needs_ai": False,
            "final_status": "EXCEPTION",
            "confidence": 0.99,
            "reason": f"Duplicate bank credit transactions ({dup_res['count']}) detected.",
            "suggested_action": "Initiate duplicate settlement recovery.",
            "tool_evidence": evidence,
            "audit_trail": audit,
        }

    # Single bank transaction found
    bank_tx = bank_res["transactions"][0]
    actual_amount = Decimal(bank_tx["amount"])
    diff = abs(expected_net - actual_amount)
    bank_desc = bank_tx.get("description", "")
    evidence.append(f"Bank credit of Rs {actual_amount} located (Ref: {bank_tx['reference']}).")

    # Clean deterministic match
    if diff == Decimal("0.00") and pay_res["customer_name"].lower() in bank_desc.lower():
        return {
            "gateway_found": True,
            "bank_found": True,
            "expected_amount": expected_net,
            "actual_amount": actual_amount,
            "difference": Decimal("0.00"),
            "needs_ai": False,
            "final_status": "MATCHED",
            "confidence": 0.99,
            "reason": "Exact deterministic match across payment, gateway, and bank ledgers.",
            "suggested_action": "No action required.",
            "tool_evidence": evidence,
            "audit_trail": audit,
        }

    # Needs investigation: Entity variation, fee mismatch, or unexplained difference
    return {
        "gateway_found": True,
        "bank_found": True,
        "customer_name": pay_res["customer_name"],
        "payment_amount": Decimal(pay_res["amount"]),
        "expected_amount": expected_net,
        "actual_amount": actual_amount,
        "difference": diff,
        "bank_description": bank_desc,
        "needs_ai": True,
        "tool_evidence": evidence,
        "audit_trail": audit,
    }


def investigate_exception_node(state: ReconciliationState) -> Dict[str, Any]:
    """Node 2: Runs investigative tools and queries Gemini with verified evidence."""
    pid = state["payment_id"]
    customer = state["customer_name"]
    diff = state.get("difference", Decimal("0.00"))
    bank_desc = state.get("bank_description", "")
    evidence = list(state.get("tool_evidence", []))
    audit = list(state.get("audit_trail", []))

    # Tool 1: Entity Match
    entity_res = match_customer_entity(customer, bank_desc)
    audit.append({"node": "investigate_exception", "tool": "match_customer_entity", "output": entity_res})
    if entity_res["matched"]:
        evidence.append(entity_res["evidence"])

    # Tool 2: Fee Explanation
    if diff > Decimal("0.00"):
        fee_res = find_fee_explanation(pid, diff)
        audit.append({"node": "investigate_exception", "tool": "find_fee_explanation", "output": fee_res})
        if fee_res["has_explanation"]:
            evidence.append(fee_res["evidence"])
        else:
            evidence.append(f"Audit confirmed: No documented fee schedule explains the Rs {diff} difference.")

    # Execute Gemini Structured Reasoning
    client = GeminiInvestigationClient()
    context = {
        "payment_id": pid,
        "customer_name": customer,
        "payment_amount": str(state.get("payment_amount", "")),
        "expected_amount": str(state.get("expected_amount", "")),
        "actual_amount": str(state.get("actual_amount", "")),
        "difference": str(diff),
        "gateway_status": "CAPTURED" if state.get("gateway_found") else "MISSING",
        "bank_status": "CREDITED" if state.get("bank_found") else "MISSING",
        "tool_evidence": evidence,
    }

    analysis = client.investigate(context)
    audit.append({"node": "investigate_exception", "tool": "gemini_model", "output": analysis.model_dump()})

    return {
        "final_status": analysis.status,
        "confidence": analysis.confidence,
        "reason": analysis.reason,
        "suggested_action": analysis.suggested_action,
        "fact_vs_hypothesis": analysis.fact_vs_hypothesis,
        "tool_evidence": evidence,
        "audit_trail": audit,
    }