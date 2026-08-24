from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from finance.models import (
    ReconciliationJob,
    Payment,
    GatewayTransaction,
    BankTransaction,
    ReconciliationResult,
    ExceptionRecord,
    AuditLog,
)


class ModelAndHealthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check_endpoint(self):
        url = reverse("system-health")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "ok")
        self.assertEqual(data["total_payments"], 0)

    def test_financial_precision_and_relationships(self):
        payment = Payment.objects.create(
            payment_id="P_PRECISION_01",
            customer_name="Infosys Technologies",
            amount=Decimal("100000.50"),
            payment_date=timezone.now().date(),
        )

        gw = GatewayTransaction.objects.create(
            gateway_transaction_id="GW_PRECISION_01",
            payment=payment,
            amount=Decimal("100000.50"),
            gateway_fee=Decimal("2000.00"),
            tax_on_fee=Decimal("360.00"),
            settlement_date=timezone.now().date(),
            status="CAPTURED",
        )

        self.assertEqual(gw.total_deductions, Decimal("2360.00"))
        self.assertEqual(gw.net_settlement_expected, Decimal("97640.50"))

        bank = BankTransaction.objects.create(
            bank_transaction_id="BNK_PRECISION_01",
            reference="P_PRECISION_01",
            amount=Decimal("97640.50"),
            transaction_date=timezone.now().date(),
        )

        result = ReconciliationResult.objects.create(
            payment=payment,
            expected_amount=gw.net_settlement_expected,
            actual_amount=bank.amount,
            difference=gw.net_settlement_expected - bank.amount,
            status="MATCHED",
            confidence=0.99,
            evidence=["Calculated expected settlement matched bank line item."],
        )

        self.assertEqual(result.difference, Decimal("0.00"))
        self.assertEqual(result.status, "MATCHED")