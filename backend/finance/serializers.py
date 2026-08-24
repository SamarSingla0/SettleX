from rest_framework import serializers
from decimal import Decimal
from .models import (
    ReconciliationJob,
    Payment,
    GatewayTransaction,
    BankTransaction,
    ReconciliationResult,
    ExceptionRecord,
    AuditLog,
    GroundTruthRecord,
)


class SystemHealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    database = serializers.CharField()
    journal_mode = serializers.CharField()
    gemini_configured = serializers.BooleanField()
    total_jobs = serializers.IntegerField()
    total_payments = serializers.IntegerField()
    total_gateway_transactions = serializers.IntegerField()
    total_bank_transactions = serializers.IntegerField()
    total_reconciliations = serializers.IntegerField()
    total_exceptions = serializers.IntegerField()
    total_audit_logs = serializers.IntegerField()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class GatewayTransactionSerializer(serializers.ModelSerializer):
    total_deductions = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    net_settlement_expected = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = GatewayTransaction
        fields = "__all__"


class BankTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransaction
        fields = "__all__"


class ReconciliationResultSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="payment.customer_name", read_only=True)
    currency = serializers.CharField(source="payment.currency", read_only=True)
    payment_amount = serializers.DecimalField(source="payment.amount", max_digits=14, decimal_places=2, read_only=True)
    payment_date = serializers.DateField(source="payment.payment_date", read_only=True)
    gateway = serializers.CharField(source="payment.gateway", read_only=True)

    class Meta:
        model = ReconciliationResult
        fields = "__all__"


class ExceptionRecordSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="payment.customer_name", read_only=True)
    payment_amount = serializers.DecimalField(source="payment.amount", max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = ExceptionRecord
        fields = "__all__"


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"


class GroundTruthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroundTruthRecord
        fields = "__all__"


class ReconciliationJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReconciliationJob
        fields = "__all__"


class GenerateDatasetRequestSerializer(serializers.Serializer):
    count = serializers.ChoiceField(choices=[50, 100, 150, 500], default=150)
    seed = serializers.IntegerField(default=42, required=False)


class RunReconciliationRequestSerializer(serializers.Serializer):
    use_ai = serializers.BooleanField(default=True, required=False)