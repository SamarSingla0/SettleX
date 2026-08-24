import uuid
from decimal import Decimal
from django.db import connection
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

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
from .serializers import (
    SystemHealthSerializer,
    PaymentSerializer,
    GatewayTransactionSerializer,
    BankTransactionSerializer,
    ReconciliationResultSerializer,
    ExceptionRecordSerializer,
    AuditLogSerializer,
    ReconciliationJobSerializer,
    GroundTruthRecordSerializer,
    GenerateDatasetRequestSerializer,
    RunReconciliationRequestSerializer,
)
from .services.dataset_generator import SyntheticDatasetGenerator
from .services.reconciliation import DeterministicReconciliationEngine
from .services.evaluation import EvaluationService
from evaluation.ground_truth import GroundTruthEvaluator
from evaluation.metrics import MetricsCalculator


class StandardResultsPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 500


class SystemHealthView(APIView):
    def get(self, request):
        db_status = "ok"
        journal_mode = "unknown"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.execute("PRAGMA journal_mode;")
                row = cursor.fetchone()
                if row:
                    journal_mode = row[0]
        except Exception as exc:
            db_status = f"unhealthy: {str(exc)}"

        gemini_key = getattr(settings, "GEMINI_API_KEY", "")
        gemini_ok = bool(gemini_key and gemini_key != "your_gemini_api_key_here")

        payload = {
            "status": "healthy" if db_status == "ok" else "degraded",
            "database": db_status,
            "journal_mode": journal_mode,
            "gemini_configured": gemini_ok,
            "total_jobs": ReconciliationJob.objects.count(),
            "total_payments": Payment.objects.count(),
            "total_gateway_transactions": GatewayTransaction.objects.count(),
            "total_bank_transactions": BankTransaction.objects.count(),
            "total_reconciliations": ReconciliationResult.objects.count(),
            "total_exceptions": ExceptionRecord.objects.count(),
            "total_audit_logs": AuditLog.objects.count(),
        }
        serializer = SystemHealthSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK if db_status == "ok" else status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateDatasetView(APIView):
    def post(self, request):
        serializer = GenerateDatasetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        count = serializer.validated_data["count"]
        seed = serializer.validated_data.get("seed", 42)

        generator = SyntheticDatasetGenerator(record_count=count, seed=seed, export_csv=True)
        stats = generator.generate()
        return Response({
            "message": f"Successfully generated {count} synthetic records.",
            "stats": stats,
        }, status=status.HTTP_201_CREATED)


class RunReconciliationView(APIView):
    def post(self, request):
        req_serializer = RunReconciliationRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)
        use_ai = req_serializer.validated_data.get("use_ai", True)

        if use_ai:
            from .services.reconciliation import FullReconciliationEngine
            engine = FullReconciliationEngine()
        else:
            from .services.reconciliation import DeterministicReconciliationEngine
            engine = DeterministicReconciliationEngine()

        summary = engine.run_batch()
        metrics = MetricsCalculator.calculate_job_metrics(summary["job_id"])
        gt_eval = GroundTruthEvaluator.evaluate_batch()

        return Response({
            "message": "Batch reconciliation executed successfully.",
            "summary": summary,
            "metrics": metrics,
            "evaluation": gt_eval,
        }, status=status.HTTP_200_OK)


class ReconciliationJobDetailView(APIView):
    def get(self, request, job_id):
        job = ReconciliationJob.objects.filter(job_id=job_id).first()
        if not job:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReconciliationJobSerializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReconciliationJobResultsView(APIView):
    def get(self, request, job_id):
        status_filter = request.query_params.get("status")
        search = request.query_params.get("search")

        results = ReconciliationResult.objects.filter(job_id=job_id).select_related("payment")
        if status_filter:
            results = results.filter(status=status_filter)
        if search:
            results = results.filter(payment__customer_name__icontains=search) | results.filter(payment__payment_id__icontains=search)

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(results, request)
        serializer = ReconciliationResultSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ReconciliationJobExceptionsView(APIView):
    def get(self, request, job_id):
        exceptions = ExceptionRecord.objects.all().select_related("payment")
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(exceptions, request)
        serializer = ExceptionRecordSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ReconciliationJobMetricsView(APIView):
    def get(self, request, job_id):
        eval_data = EvaluationService.run_evaluation(job_id)
        return Response(eval_data, status=status.HTTP_200_OK)


class EvaluationOverviewView(APIView):
    def get(self, request):
        latest_job = ReconciliationJob.objects.first()
        job_id = str(latest_job.job_id) if latest_job else None
        gt_eval = GroundTruthEvaluator.evaluate_batch()
        metrics = MetricsCalculator.calculate_job_metrics(job_id) if job_id else {}

        return Response({
            "latest_job_id": job_id,
            "metrics": metrics,
            "ground_truth_evaluation": gt_eval,
        }, status=status.HTTP_200_OK)


class TransactionDetailView(APIView):
    def get(self, request, payment_id):
        payment = Payment.objects.filter(payment_id=payment_id).first()
        if not payment:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        gateway_tx = GatewayTransaction.objects.filter(payment=payment).first()
        bank_txs = list(BankTransaction.objects.filter(reference__icontains=payment_id))
        rec_result = ReconciliationResult.objects.filter(payment=payment).first()
        exceptions = ExceptionRecord.objects.filter(payment=payment)
        ground_truth = GroundTruthRecord.objects.filter(payment_id=payment_id).first()

        return Response({
            "payment": PaymentSerializer(payment).data,
            "gateway_transaction": GatewayTransactionSerializer(gateway_tx).data if gateway_tx else None,
            "bank_transactions": BankTransactionSerializer(bank_txs, many=True).data,
            "reconciliation_result": ReconciliationResultSerializer(rec_result).data if rec_result else None,
            "exceptions": ExceptionRecordSerializer(exceptions, many=True).data,
            "ground_truth": GroundTruthRecordSerializer(ground_truth).data if ground_truth else None,
        }, status=status.HTTP_200_OK)


class TransactionAuditLogsView(APIView):
    def get(self, request, payment_id):
        logs = AuditLog.objects.filter(payment_id=payment_id).order_by("created_at")
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)