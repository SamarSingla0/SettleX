from django.urls import path
from .views import (
    SystemHealthView,
    GenerateDatasetView,
    RunReconciliationView,
    ReconciliationJobDetailView,
    ReconciliationJobResultsView,
    ReconciliationJobExceptionsView,
    ReconciliationJobMetricsView,
    EvaluationOverviewView,
    TransactionDetailView,
    TransactionAuditLogsView,
)

urlpatterns = [
    path("health/", SystemHealthView.as_view(), name="system-health"),
    path("datasets/generate/", GenerateDatasetView.as_view(), name="generate-dataset"),
    path("reconciliation/run/", RunReconciliationView.as_view(), name="reconciliation-run"),
    path("reconciliation/<uuid:job_id>/", ReconciliationJobDetailView.as_view(), name="job-detail"),
    path("reconciliation/<uuid:job_id>/results/", ReconciliationJobResultsView.as_view(), name="job-results"),
    path("reconciliation/<uuid:job_id>/exceptions/", ReconciliationJobExceptionsView.as_view(), name="job-exceptions"),
    path("reconciliation/<uuid:job_id>/metrics/", ReconciliationJobMetricsView.as_view(), name="job-metrics"),
    path("evaluation/overview/", EvaluationOverviewView.as_view(), name="evaluation-overview"),
    path("transactions/<str:payment_id>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("transactions/<str:payment_id>/audit/", TransactionAuditLogsView.as_view(), name="transaction-audit"),
]