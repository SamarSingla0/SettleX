from decimal import Decimal
from django.core.management.base import BaseCommand
from finance.services.gemini_client import GeminiInvestigationClient


class Command(BaseCommand):
    help = "Tests Gemini connection and verifies structured Pydantic schema validation."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(">>> Testing Gemini Structured Investigation Client..."))

        client = GeminiInvestigationClient()
        if not client.configured:
            self.stdout.write(self.style.WARNING("[!] GEMINI_API_KEY is missing or set to placeholder in .env."))
            self.stdout.write("[*] Testing safe fallback execution...")

        # Test Context: Rs 500 dispute fee discrepancy
        test_context = {
            "payment_id": "P0042",
            "customer_name": "Infosys Technologies",
            "payment_amount": Decimal("25000.00"),
            "expected_amount": Decimal("24410.00"),
            "actual_amount": Decimal("23910.00"),
            "difference": Decimal("500.00"),
            "gateway_status": "CAPTURED",
            "bank_status": "CREDITED",
            "tool_evidence": [
                "Payment P0042 captured via Razorpay",
                "Bank credited Rs 23,910 on 2026-08-02",
                "Gateway audit log confirms Rs 500 interchange dispute handling fee deduction",
            ],
        }

        analysis = client.investigate(test_context)

        self.stdout.write(self.style.SUCCESS("[+] Structured Output received and validated by Pydantic:"))
        self.stdout.write(f"    - Status             : {analysis.status}")
        self.stdout.write(f"    - Confidence         : {analysis.confidence:.2f}")
        self.stdout.write(f"    - Reason             : {analysis.reason}")
        self.stdout.write(f"    - Suggested Action   : {analysis.suggested_action}")
        self.stdout.write(f"    - Fact vs Hypothesis : {analysis.fact_vs_hypothesis}")
        self.stdout.write(f"    - Evidence Count     : {len(analysis.evidence)}")