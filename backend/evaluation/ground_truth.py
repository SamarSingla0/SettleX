from typing import Dict, Any, List
from finance.models import GroundTruthRecord, ReconciliationResult


class GroundTruthEvaluator:
    """
    Compares runtime reconciliation results against verified ground truth records.
    Computes strict multiclass classification Accuracy, Precision, Recall, and Match Rates.
    """

    @staticmethod
    def evaluate_batch() -> Dict[str, Any]:
        ground_truth_map = {gt.payment_id: gt for gt in GroundTruthRecord.objects.all()}
        results = list(ReconciliationResult.objects.all())

        total = len(ground_truth_map)
        if total == 0:
            return {
                "total_records": 0,
                "evaluated_records": len(results),
                "correct_classifications": 0,
                "accuracy_pct": 0.0,
                "match_rate_pct": 0.0,
                "precision_pct": 0.0,
                "recall_pct": 0.0,
                "true_positives": 0,
                "false_positives": 0,
                "false_negatives": 0,
                "true_negatives": 0,
                "avg_confidence_pct": 0.0,
                "breakdown": {"matched": 0, "resolved": 0, "exceptions": 0, "unresolved": 0},
                "discrepancies_count": 0,
                "discrepancies": [],
                "error": "No ground truth records found in database.",
            }

        correct_classifications = 0
        matched_count = 0
        resolved_count = 0
        exception_count = 0
        unresolved_count = 0

        tp = 0  # Expected positive, classified positive
        fp = 0  # Expected negative, classified positive
        fn = 0  # Expected positive, classified negative
        tn = 0  # Expected negative, classified negative

        confidence_sum = 0.0
        discrepancies: List[Dict[str, Any]] = []

        for result in results:
            gt = ground_truth_map.get(result.payment_id)
            if not gt:
                continue

            confidence_sum += result.confidence

            if result.status in ["MATCHED", "MATCHED_DELAYED"]:
                matched_count += 1
            elif result.status == "RESOLVED":
                resolved_count += 1
            elif result.status == "EXCEPTION":
                exception_count += 1
            elif result.status == "UNRESOLVED":
                unresolved_count += 1

            is_correct = (result.status == gt.expected_status)
            if is_correct:
                correct_classifications += 1
            else:
                discrepancies.append({
                    "payment_id": result.payment_id,
                    "expected_status": gt.expected_status,
                    "actual_status": result.status,
                    "scenario": gt.scenario_type,
                    "confidence": result.confidence,
                    "reason": result.reason,
                })

            is_actual_positive = result.status in ["MATCHED", "MATCHED_DELAYED", "RESOLVED"]
            is_expected_positive = gt.expected_status in ["MATCHED", "MATCHED_DELAYED", "RESOLVED"]

            if is_actual_positive and is_expected_positive:
                tp += 1
            elif is_actual_positive and not is_expected_positive:
                fp += 1
            elif not is_actual_positive and is_expected_positive:
                fn += 1
            else:
                tn += 1

        accuracy = (correct_classifications / total) * 100 if total > 0 else 0.0
        match_rate = ((matched_count + resolved_count) / total) * 100 if total > 0 else 0.0
        avg_confidence = (confidence_sum / len(results)) * 100 if len(results) > 0 else 0.0

        precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0.0
        recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0.0

        return {
            "total_records": total,
            "evaluated_records": len(results),
            "correct_classifications": correct_classifications,
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
                "matched": matched_count,
                "resolved": resolved_count,
                "exceptions": exception_count,
                "unresolved": unresolved_count,
            },
            "discrepancies_count": len(discrepancies),
            "discrepancies": discrepancies[:10],
        }