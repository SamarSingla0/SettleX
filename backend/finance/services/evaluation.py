from typing import Dict, Any
from evaluation.ground_truth import GroundTruthEvaluator
from evaluation.metrics import MetricsCalculator


class EvaluationService:
    """
    Facade service linking Django ORM jobs to Ground Truth evaluation modules.
    """

    @staticmethod
    def run_evaluation(job_id: str) -> Dict[str, Any]:
        metrics = MetricsCalculator.calculate_job_metrics(job_id)
        ground_truth_stats = GroundTruthEvaluator.evaluate_batch()
        return {
            "job_metrics": metrics,
            "ground_truth_validation": ground_truth_stats,
        }