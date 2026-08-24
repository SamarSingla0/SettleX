from typing import Dict, Any, List
from django.db.models import Avg
from finance.models import ReconciliationResult, GroundTruthRecord, ReconciliationJob


class MetricsCalculator:
    """
    Computes rigorous financial ops reconciliation and classification metrics.
    """

    @staticmethod
    def calculate_job_metrics(job_id: str) -> Dict[str, Any]:
        job = ReconciliationJob.objects.filter(job_id=job_id).first()
        if not job:
            return {"error": f"Job {job_id} not found."}

        results = list(ReconciliationResult.objects.filter(job=job))
        gt_records = {gt.payment_id: gt for gt in GroundTruthRecord.objects.all()}

        total = len(results)
        if total == 0:
            return {"error": "No reconciliation results available for evaluation."}

        correct_count = 0
        conf_sum = 0.0

        tp = 0
        fp = 0
        fn = 0
        tn = 0

        for r in results:
            conf_sum += r.confidence
            gt = gt_records.get(r.payment_id)
            if not gt:
                continue

            if r.status == gt.expected_status:
                correct_count += 1

            is_actual_auto = r.status in ["MATCHED", "MATCHED_DELAYED", "RESOLVED"]
            is_expected_auto = gt.expected_status in ["MATCHED", "MATCHED_DELAYED", "RESOLVED"]

            if is_actual_auto and is_expected_auto:
                tp += 1
            elif is_actual_auto and not is_expected_auto:
                fp += 1
            elif not is_actual_auto and is_expected_auto:
                fn += 1
            else:
                tn += 1

        accuracy = (correct_count / total) * 100 if total > 0 else 0.0
        match_rate = ((job.matched_records + job.resolved_records) / total) * 100 if total > 0 else 0.0
        avg_confidence = (conf_sum / total) * 100 if total > 0 else 0.0

        precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0.0
        recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0.0

        job.accuracy = round(accuracy, 2)
        job.avg_confidence = round(avg_confidence, 2)
        job.match_rate = round(match_rate, 2)
        job.save()

        return {
            "job_id": str(job.job_id),
            "total_records": total,
            "accuracy_pct": round(accuracy, 2),
            "match_rate_pct": round(match_rate, 2),
            "precision_pct": round(precision, 2),
            "recall_pct": round(recall, 2),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "avg_confidence_pct": round(avg_confidence, 2),
            "breakdown": {
                "matched": job.matched_records,
                "resolved": job.resolved_records,
                "exceptions": job.exception_records,
                "unresolved": job.unresolved_records,
            },
        }