from django.core.management.base import BaseCommand
from finance.services.reconciliation import FullReconciliationEngine
from evaluation.ground_truth import GroundTruthEvaluator
from evaluation.metrics import MetricsCalculator


class Command(BaseCommand):
    help = "Executes full LangGraph agent reconciliation across 150 records."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(">>> Starting Phase 6: LangGraph Agent Batch Reconciliation..."))

        engine = FullReconciliationEngine()
        summary = engine.run_batch()

        self.stdout.write(self.style.SUCCESS(f"[+] Processed {summary['total_records']} records through LangGraph:"))
        self.stdout.write(f"    - Matched Records  : {summary['matched_records']}")
        self.stdout.write(f"    - AI Resolved      : {summary['resolved_records']}")
        self.stdout.write(f"    - Exceptions       : {summary['exception_records']}")
        self.stdout.write(f"    - Unresolved Cases : {summary['unresolved_records']}")
        self.stdout.write(f"    - Match Rate       : {summary['match_rate_pct']}%")

        # Evaluate against Ground Truth
        metrics = MetricsCalculator.calculate_job_metrics(summary["job_id"])
        gt_eval = GroundTruthEvaluator.evaluate_batch()

        self.stdout.write(self.style.NOTICE("\n>>> Evaluation against Ground Truth (Post-AI):"))
        self.stdout.write(f"[*] Accuracy Rate      : {gt_eval['accuracy_pct']}%")
        self.stdout.write(f"[*] Precision Rate     : {gt_eval['precision_pct']}%")
        self.stdout.write(f"[*] Recall Rate        : {gt_eval['recall_pct']}%")
        self.stdout.write(f"[*] Average Confidence : {gt_eval['avg_confidence_pct']}%")