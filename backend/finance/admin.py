from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ReconciliationJob,
    Payment,
    GatewayTransaction,
    BankTransaction,
    ReconciliationResult,
    ExceptionRecord,
    AuditLog,
)


@admin.register(ReconciliationJob)
class ReconciliationJobAdmin(admin.ModelAdmin):
    list_display = (
        "job_id",
        "status_badge",
        "total_records",
        "matched_records",
        "resolved_records",
        "exception_records",
        "unresolved_records",
        "match_rate_pct",
        "accuracy_pct",
        "started_at",
    )
    list_filter = ("status", "started_at")
    readonly_fields = ("job_id", "started_at", "completed_at")
    search_fields = ("job_id",)

    def status_badge(self, obj):
        colors = {
            "COMPLETED": "#22c55e",
            "PROCESSING": "#3b82f6",
            "PENDING": "#eab308",
            "FAILED": "#ef4444",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.status,
        )
    status_badge.short_description = "Status"

    def match_rate_pct(self, obj):
        return f"{obj.match_rate:.1f}%"
    match_rate_pct.short_description = "Match Rate"

    def accuracy_pct(self, obj):
        return f"{obj.accuracy:.1f}%"
    accuracy_pct.short_description = "Accuracy"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "customer_name", "amount", "currency", "payment_date", "gateway", "created_at")
    search_fields = ("payment_id", "customer_name")
    list_filter = ("currency", "gateway", "payment_date")


@admin.register(GatewayTransaction)
class GatewayTransactionAdmin(admin.ModelAdmin):
    list_display = ("gateway_transaction_id", "payment", "amount", "gateway_fee", "tax_on_fee", "settlement_date", "status")
    search_fields = ("gateway_transaction_id", "payment__payment_id")
    list_filter = ("status", "settlement_date")


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ("bank_transaction_id", "reference", "amount", "transaction_date", "bank_name")
    search_fields = ("bank_transaction_id", "reference", "description")
    list_filter = ("bank_name", "transaction_date")


@admin.register(ReconciliationResult)
class ReconciliationResultAdmin(admin.ModelAdmin):
    list_display = ("payment", "expected_amount", "actual_amount", "difference", "status", "confidence_pct", "created_at")
    list_filter = ("status",)
    search_fields = ("payment__payment_id", "reason")

    def confidence_pct(self, obj):
        return f"{obj.confidence * 100:.1f}%"
    confidence_pct.short_description = "Confidence"


@admin.register(ExceptionRecord)
class ExceptionRecordAdmin(admin.ModelAdmin):
    list_display = ("payment", "exception_type", "resolved", "created_at")
    list_filter = ("exception_type", "resolved")
    search_fields = ("payment__payment_id", "reason")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "payment", "job_id", "agent_node", "tool_called")
    list_filter = ("agent_node", "tool_called", "created_at")
    search_fields = ("payment__payment_id", "job_id", "notes")
    readonly_fields = ("created_at",)
    
    
    
from .models import GroundTruthRecord  # Add to existing imports

@admin.register(GroundTruthRecord)
class GroundTruthRecordAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "customer_name", "scenario_type", "expected_status", "expected_difference", "is_resolvable")
    list_filter = ("expected_status", "scenario_type", "is_resolvable")
    search_fields = ("payment_id", "customer_name", "scenario_type")