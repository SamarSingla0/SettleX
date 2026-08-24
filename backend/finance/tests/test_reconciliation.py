from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from finance.models import (
    Payment,
    GatewayTransaction,
    BankTransaction,
    ReconciliationResult,
    ExceptionRecord,
)
from finance.services.reconciliation import DeterministicReconciliationEngine


class DeterministicReconciliationTestCase(TestCase):
    def setUp(self):
        self.engine = DeterministicReconciliationEngine()
        self.today = date(2026, 8, 1)

    def test_exact_match(self):
        payment = Payment.objects.create(
            payment_id="TEST_EXACT_01",
            customer_name="Tata Consultancy Services",
            amount=Decimal("10000.00"),
            payment_date=self.today,
        )
        GatewayTransaction.objects.create(
            gateway_transaction_id="GTW_TEST_EXACT_01",
            payment=payment,
            amount=Decimal("10000.00"),
            gateway_fee=Decimal("200.00"),
            tax_on_fee=Decimal("36.00"),
            settlement_date=self.today + timedelta(days=1),
            status="CAPTURED",
        )
        BankTransaction.objects.create(
            bank_transaction_id="BTX_TEST_EXACT_01",
            reference="RAZORPAY_SETTLE_TEST_EXACT_01",
            amount=Decimal("9764.00"),
            transaction_date=self.today + timedelta(days=1),
        )

        decision = self.engine.reconcile_payment(payment)
        self.assertEqual(decision["status"], "MATCHED")
        self.assertEqual(decision["difference"], Decimal("0.00"))
        self.assertEqual(decision["confidence"], 0.99)

    def test_amount_mismatch_exception(self):
        payment = Payment.objects.create(
            payment_id="TEST_MISMATCH_01",
            customer_name="Infosys Technologies",
            amount=Decimal("20000.00"),
            payment_date=self.today,
        )
        GatewayTransaction.objects.create(
            gateway_transaction_id="GTW_TEST_MISMATCH_01",
            payment=payment,
            amount=Decimal("20000.00"),
            gateway_fee=Decimal("400.00"),
            tax_on_fee=Decimal("72.00"),
            settlement_date=self.today + timedelta(days=1),
            status="CAPTURED",
        )
        # Bank received Rs 500 less than the expected 19528.00
        BankTransaction.objects.create(
            bank_transaction_id="BTX_TEST_MISMATCH_01",
            reference="RAZORPAY_NET_TEST_MISMATCH_01",
            amount=Decimal("19028.00"),
            transaction_date=self.today + timedelta(days=1),
        )

        decision = self.engine.reconcile_payment(payment)
        self.assertEqual(decision["status"], "EXCEPTION")
        self.assertEqual(decision["difference"], Decimal("500.00"))
        self.assertEqual(decision["exception_type"], "AMOUNT_MISMATCH")

    def test_duplicate_bank_transaction_exception(self):
        payment = Payment.objects.create(
            payment_id="TEST_DUP_01",
            customer_name="Reliance Retail Ltd",
            amount=Decimal("5000.00"),
            payment_date=self.today,
        )
        GatewayTransaction.objects.create(
            gateway_transaction_id="GTW_TEST_DUP_01",
            payment=payment,
            amount=Decimal("5000.00"),
            gateway_fee=Decimal("100.00"),
            tax_on_fee=Decimal("18.00"),
            settlement_date=self.today + timedelta(days=1),
            status="CAPTURED",
        )
        # Two identical credits in bank ledger
        BankTransaction.objects.create(
            bank_transaction_id="BTX_DUP_A",
            reference="RAZORPAY_DUP_TEST_DUP_01",
            amount=Decimal("4882.00"),
            transaction_date=self.today + timedelta(days=1),
        )
        BankTransaction.objects.create(
            bank_transaction_id="BTX_DUP_B",
            reference="RAZORPAY_DUP_TEST_DUP_01",
            amount=Decimal("4882.00"),
            transaction_date=self.today + timedelta(days=1),
        )

        decision = self.engine.reconcile_payment(payment)
        self.assertEqual(decision["status"], "EXCEPTION")
        self.assertEqual(decision["exception_type"], "DUPLICATE_SETTLEMENT")

    def test_missing_gateway_record(self):
        payment = Payment.objects.create(
            payment_id="TEST_MISSING_GW_01",
            customer_name="Swiggy Bundl Technologies",
            amount=Decimal("1500.00"),
            payment_date=self.today,
        )
        # No Gateway transaction created

        decision = self.engine.reconcile_payment(payment)
        self.assertEqual(decision["status"], "UNRESOLVED")
        self.assertEqual(decision["exception_type"], "MISSING_GATEWAY_RECORD")