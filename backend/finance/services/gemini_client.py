import os
import json
import logging
from typing import List, Literal, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from django.conf import settings

logger = logging.getLogger(__name__)


class InvestigationAnalysisSchema(BaseModel):
    """
    Strict Pydantic schema for structured output from Gemini.
    """
    status: Literal["RESOLVED", "MATCHED_DELAYED", "EXCEPTION", "UNRESOLVED"] = Field(
        description="Reconciliation verdict. Must be UNRESOLVED if proof is missing."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 based strictly on verified evidence.",
    )
    reason: str = Field(
        description="Concise, factual explanation citing exact numbers or entity variations."
    )
    evidence: List[str] = Field(
        description="List of verified facts discovered from database tools."
    )
    suggested_action: str = Field(
        description="Operational next step for finance ops."
    )
    fact_vs_hypothesis: str = Field(
        description="Clearly state what is verified FACT vs UNKNOWN."
    )


class GeminiInvestigationClient:
    """
    Client interface for Gemini API structured investigations.
    """

    SYSTEM_PROMPT = """You are the Senior AI Payment Settlement Controller at a Tier-1 FinTech.
Your responsibility is to investigate payment reconciliation exceptions with zero financial hallucinations.

STRICT OPERATING RULES:
1. NEVER invent transactions, bank fees, chargebacks, or settlements that are not explicitly provided in the evidence.
2. If bank settlement is absent, the status MUST be 'UNRESOLVED'. Reason: 'No corresponding bank settlement was found.'
3. If an amount discrepancy has NO verified fee or deduction record, the status MUST be 'UNRESOLVED'.
4. Distinguish clearly between FACT (verified in data) and UNKNOWN.
5. Entity variations (e.g., 'TCS Ltd' vs 'Tata Consultancy Services') can be RESOLVED if amounts, dates, and gateway references align.
6. Return structured JSON strictly adhering to the schema.
"""

    def __init__(self):
        api_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
        self.configured = bool(api_key and api_key != "your_gemini_api_key_here")
        self.client = genai.Client(api_key=api_key) if self.configured else None
        # Default to active flash model
        self.model_name = getattr(settings, "GEMINI_MODEL", "gemini-3.6-flash")

    def investigate(self, context: Dict[str, Any]) -> InvestigationAnalysisSchema:
        if not self.configured or not self.client:
            logger.warning("Gemini API key not configured. Returning fallback safe decision.")
            return self._fallback_decision(context, reason="Gemini API key missing or unconfigured.")

        user_prompt = f"""Investigate this reconciliation exception:

TRANSACTION DETAILS:
- Payment ID: {context.get('payment_id')}
- Customer Name: {context.get('customer_name')}
- Payment Amount: Rs {context.get('payment_amount')}
- Expected Net Settlement: Rs {context.get('expected_amount')}
- Actual Bank Settlement: Rs {context.get('actual_amount')}
- Difference: Rs {context.get('difference')}
- Gateway Record Status: {context.get('gateway_status')}
- Bank Record Status: {context.get('bank_status')}

INVESTIGATION TOOL OUTPUTS & EVIDENCE:
{json.dumps(context.get('tool_evidence', []), indent=2)}

Analyze the evidence and provide the reconciliation verdict.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=InvestigationAnalysisSchema,
                    temperature=0.1,
                ),
            )

            parsed_json = json.loads(response.text)
            return InvestigationAnalysisSchema(**parsed_json)

        except Exception as exc:
            logger.error(f"Gemini generation error: {str(exc)}")
            return self._fallback_decision(context, reason=f"AI Investigation failed: {str(exc)}")

    def _fallback_decision(self, context: Dict[str, Any], reason: str) -> InvestigationAnalysisSchema:
        return InvestigationAnalysisSchema(
            status="UNRESOLVED",
            confidence=0.60,
            reason=f"Unresolved exception: {reason}",
            evidence=context.get("tool_evidence", ["Manual inspection required."]),
            suggested_action="Escalate to human finance analyst.",
            fact_vs_hypothesis="FACT: Discrepancy observed. UNKNOWN: Root cause.",
        )