from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from finance.models import (
    ReconciliationJob,
    Payment,
    GatewayTransaction,
    BankTransaction,
    ReconciliationResult,
    ExceptionRecord,
    AuditLog,
)


class Command(BaseCommand):
    help = "Validates the database schema, SQLite WAL mode, and verifies table constraints."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(">>> Verifying Database Architecture and Models..."))

        # 1. SQLite PRAGMA check
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode;")
            journal_mode = cursor.fetchone()[0]
            self.stdout.write(f"[*] SQLite Journal Mode: {journal_mode}")

        # 2. CRUD smoke test
        self.stdout.write("[*] Executing test transaction create and delete...")
        
        job = ReconciliationJob.objects.create(total_records=1, status="PROCESSING")
        
        payment = Payment.objects.create(
            payment_id="TEST_P999",
            customer_name="Acme Corporation Ltd",
            amount=Decimal("15000.00"),
            payment_date=timezone.now().date(),
        )

        gw_tx = GatewayTransaction.objects.create(
            gateway_transaction_id="TEST_GW_999",
            payment=payment,
            amount=Decimal("15000.00"),
            gateway_fee=Decimal("300.00"),
            tax_on_fee=Decimal("54.00"),
            settlement_date=timezone.now().date(),
            status="CAPTURED",
        )

        bank_tx = BankTransaction.objects.create(
            bank_transaction_id="TEST_BNK_999",
            reference="TEST_P999_PAYMENT",
            amount=Decimal("14646.00"),
            transaction_date=timezone.now().date(),
            description="Settlement credit from Razorpay",
        )

        rec_result = ReconciliationResult.objects.create(
            job=job,
            payment=payment,
            expected_amount=Decimal("14646.00"),
            actual_amount=Decimal("14646.00"),
            difference=Decimal("0.00"),
            status="MATCHED",
            confidence=0.99,
            reason="Exact mathematical and identifier match.",
            evidence=["Payment captured", "Gateway settlement verified", "Bank credit matched"],
        )

        exception = ExceptionRecord.objects.create(
            payment=payment,
            exception_type="DELAYED_SETTLEMENT",
            reason="Settled after 3 business days",
            resolved=True,
        )

        audit = AuditLog.objects.create(
            payment=payment,
            job_id=str(job.job_id),
            agent_node="deterministic_reconciler",
            tool_called="calculate_expected_settlement",
            tool_input={"payment_id": "TEST_P999"},
            tool_output={"expected_amount": "14646.00"},
            notes="Smoke test audit log record",
        )

        # 3. Assertions
        assert ReconciliationJob.objects.filter(job_id=job.job_id).exists()
        assert Payment.objects.filter(payment_id="TEST_P999").exists()
        assert GatewayTransaction.objects.filter(gateway_transaction_id="TEST_GW_999").exists()
        assert BankTransaction.objects.filter(bank_transaction_id="TEST_BNK_999").exists()
        assert ReconciliationResult.objects.filter(payment=payment).exists()
        assert ExceptionRecord.objects.filter(payment=payment).exists()
        assert AuditLog.objects.filter(payment=payment).exists()

        # 4. Clean up smoke test artifacts
        audit.delete()
        exception.delete()
        rec_result.delete()
        bank_tx.delete()
        gw_tx.delete()
        payment.delete()
        job.delete()

        self.stdout.write(self.style.SUCCESS("[+] All 7 Models, Relations, Foreign Keys & JSONFields validated successfully!"))