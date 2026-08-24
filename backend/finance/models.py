import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone


class ReconciliationJob(models.Model):
    """
    Tracks lifecycle, progress, and aggregated metrics of batch reconciliation jobs.
    """
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    total_records = models.PositiveIntegerField(default=0)
    matched_records = models.PositiveIntegerField(default=0)
    resolved_records = models.PositiveIntegerField(default=0)
    exception_records = models.PositiveIntegerField(default=0)
    unresolved_records = models.PositiveIntegerField(default=0)
    
    match_rate = models.FloatField(default=0.0, help_text="Percentage of auto-reconciled records")
    accuracy = models.FloatField(default=0.0, help_text="Classification accuracy against ground truth")
    avg_confidence = models.FloatField(default=0.0, help_text="Average agent confidence score (0-100)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING", db_index=True)
    error_message = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Reconciliation Job"
        verbose_name_plural = "Reconciliation Jobs"

    def __str__(self):
        return f"Job {str(self.job_id)[:8]} [{self.status}] Total: {self.total_records}"


class Payment(models.Model):
    """
    Represents customer checkout payments originating from the core billing system.
    """
    payment_id = models.CharField(max_length=64, primary_key=True, help_text="Internal ID e.g. P001")
    customer_name = models.CharField(max_length=255, db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, help_text="Gross customer payment amount")
    currency = models.CharField(max_length=10, default="INR")
    payment_date = models.DateField(db_index=True)
    gateway = models.CharField(max_length=50, default="RAZORPAY", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "payment_id"]
        verbose_name = "Customer Payment"
        verbose_name_plural = "Customer Payments"

    def __str__(self):
        return f"{self.payment_id} | {self.customer_name} | {self.currency} {self.amount}"


class GatewayTransaction(models.Model):
    """
    Represents processed transactions as recorded by payment gateways (Stripe, Razorpay, etc.).
    """
    STATUS_CHOICES = [
        ("CAPTURED", "Captured"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    gateway_transaction_id = models.CharField(max_length=64, primary_key=True, help_text="e.g. pay_gtw_001")
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="gateway_transactions",
        null=True,
        blank=True,
        help_text="Mapped payment reference (can be null for rogue/orphaned gateway transactions)",
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    gateway_fee = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    tax_on_fee = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    settlement_date = models.DateField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="CAPTURED", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-settlement_date", "gateway_transaction_id"]
        verbose_name = "Gateway Transaction"
        verbose_name_plural = "Gateway Transactions"

    def __str__(self):
        return f"GW: {self.gateway_transaction_id} -> Payment: {self.payment_id or 'UNLINKED'}"

    @property
    def total_deductions(self) -> Decimal:
        return self.gateway_fee + self.tax_on_fee

    @property
    def net_settlement_expected(self) -> Decimal:
        return self.amount - self.total_deductions


class BankTransaction(models.Model):
    """
    Represents actual credits entering corporate bank settlement accounts.
    """
    bank_transaction_id = models.CharField(max_length=64, primary_key=True, help_text="e.g. btx_001")
    reference = models.CharField(max_length=128, db_index=True, help_text="Bank statement description / UTR / Reference")
    amount = models.DecimalField(max_digits=14, decimal_places=2, help_text="Net amount credited to bank")
    transaction_date = models.DateField(db_index=True)
    description = models.TextField(blank=True, null=True)
    bank_name = models.CharField(max_length=100, default="HDFC Bank", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-transaction_date", "bank_transaction_id"]
        verbose_name = "Bank Transaction"
        verbose_name_plural = "Bank Transactions"

    def __str__(self):
        return f"BankTX: {self.bank_transaction_id} | {self.amount} | Ref: {self.reference}"


class ReconciliationResult(models.Model):
    """
    Stores deterministic & AI reconciliation decisions, confidence scores, and reasoning.
    """
    STATUS_CHOICES = [
        ("MATCHED", "Matched"),
        ("MATCHED_DELAYED", "Matched (Delayed Settlement)"),
        ("RESOLVED", "Resolved by AI"),
        ("EXCEPTION", "Exception Detected"),
        ("UNRESOLVED", "Unresolved / Escalated to Human"),
    ]

    job = models.ForeignKey(
        ReconciliationJob,
        on_delete=models.CASCADE,
        related_name="results",
        null=True,
        blank=True,
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name="reconciliation_result",
        primary_key=True,
    )
    expected_amount = models.DecimalField(max_digits=14, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    difference = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="EXCEPTION", db_index=True)
    confidence = models.FloatField(default=0.0, help_text="Confidence between 0.00 and 1.00")
    reason = models.TextField(blank=True, null=True)
    suggested_action = models.TextField(blank=True, null=True)
    evidence = models.JSONField(default=list, blank=True, help_text="List of verifiable facts found during audit")
    llm_response = models.JSONField(default=dict, blank=True, help_text="Validated structured response from Gemini")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Reconciliation Result"
        verbose_name_plural = "Reconciliation Results"

    def __str__(self):
        return f"Result: {self.payment_id} | {self.status} | Diff: {self.difference} | Conf: {self.confidence:.2f}"


class ExceptionRecord(models.Model):
    """
    Itemized exception records for workflow routing, investigations, and audit escalations.
    """
    EXCEPTION_TYPES = [
        ("AMOUNT_MISMATCH", "Amount Mismatch"),
        ("MISSING_BANK_TRANSACTION", "Missing Bank Settlement"),
        ("MISSING_GATEWAY_RECORD", "Missing Gateway Record"),
        ("DELAYED_SETTLEMENT", "Delayed Settlement"),
        ("DUPLICATE_SETTLEMENT", "Duplicate Settlement"),
        ("NAME_MISMATCH", "Customer/Entity Name Variation"),
        ("UNEXPLAINED_FEE", "Unexplained Bank/Gateway Deductions"),
        ("UNKNOWN", "Unknown Exception"),
    ]

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="exceptions",
    )
    exception_type = models.CharField(max_length=50, choices=EXCEPTION_TYPES, db_index=True)
    reason = models.TextField()
    suggested_action = models.TextField(blank=True, null=True)
    resolved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Exception Record"
        verbose_name_plural = "Exception Records"

    def __str__(self):
        return f"Exception [{self.exception_type}] on Payment: {self.payment_id}"


class AuditLog(models.Model):
    """
    Immutable step-by-step audit record tracking all deterministic rules, LangGraph node executions, and tool calls.
    """
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        null=True,
        blank=True,
    )
    job_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    agent_node = models.CharField(max_length=100, db_index=True, help_text="e.g. deterministic_match, gemini_investigate")
    tool_called = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    tool_input = models.JSONField(default=dict, blank=True)
    tool_output = models.JSONField(default=dict, blank=True)
    llm_response = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"[{self.created_at.strftime('%H:%M:%S')}] {self.payment_id or 'BATCH'} -> {self.agent_node} ({self.tool_called or 'No tool'})"
    
    
    
    
class GroundTruthRecord(models.Model):
    """
    Ground-truth reference table mapping expected reconciliation outcomes for synthetic datasets.
    """
    EXPECTED_STATUS_CHOICES = [
        ("MATCHED", "Matched"),
        ("MATCHED_DELAYED", "Matched Delayed"),
        ("RESOLVED", "Resolved"),
        ("EXCEPTION", "Exception"),
        ("UNRESOLVED", "Unresolved"),
    ]

    payment_id = models.CharField(max_length=64, primary_key=True)
    customer_name = models.CharField(max_length=255)
    scenario_type = models.CharField(max_length=64, help_text="e.g. EXACT_MATCH, ENTITY_VARIATION, MISSING_BANK")
    expected_status = models.CharField(max_length=32, choices=EXPECTED_STATUS_CHOICES)
    expected_confidence = models.FloatField(default=0.95)
    expected_difference = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    expected_reason = models.TextField()
    is_resolvable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["payment_id"]
        verbose_name = "Ground Truth Record"
        verbose_name_plural = "Ground Truth Records"

    def __str__(self):
        return f"GroundTruth: {self.payment_id} -> {self.expected_status} ({self.scenario_type})"