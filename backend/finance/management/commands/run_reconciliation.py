from django.core.management.base import BaseCommand
from finance.services.reconciliation import DeterministicReconciliationEngine
from evaluation.ground_truth import GroundTruthEvaluator
from evaluation.metrics import MetricsCalculator


class Command(BaseCommand):
    help = "Executes deterministic payment settlement reconciliation without AI."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(">>> Starting Phase 3: Deterministic Reconciliation Run..."))

        engine = DeterministicReconciliationEngine()
        summary = engine.run_batch()

        self.stdout.write(self.style.SUCCESS(f"[+] Reconciled {summary['total_records']} records:"))
        self.stdout.write(f"    - Matched (Clean & Delayed) : {summary['matched_records']}")
        self.stdout.write(f"    - Exceptions Flagged        : {summary['exception_records']}")
        self.stdout.write(f"    - Unresolved Cases          : {summary['unresolved_records']}")
        self.stdout.write(f"    - Base Match Rate           : {summary['match_rate_pct']}%")

        # Evaluate against Ground Truth
        metrics = MetricsCalculator.calculate_job_metrics(summary["job_id"])
        gt_eval = GroundTruthEvaluator.evaluate_batch()

        self.stdout.write(self.style.NOTICE("\n>>> Evaluation against Ground Truth (Pre-AI Baseline):"))
        self.stdout.write(f"[*] Total Evaluated        : {gt_eval.get('evaluated_records', 0)} / {gt_eval.get('total_records', 0)}")
        self.stdout.write(f"[*] Deterministic Accuracy : {gt_eval.get('accuracy_pct', 0.0)}%")
        self.stdout.write(f"[*] Base Match Rate        : {gt_eval.get('match_rate_pct', 0.0)}%")
        self.stdout.write(f"[*] Average Confidence     : {gt_eval.get('avg_confidence_pct', 0.0)}%")
        self.stdout.write(f"[*] Discrepancies Pending  : {gt_eval.get('discrepancies_count', 0)} (To be investigated by AI)")