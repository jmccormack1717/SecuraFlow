"""Model performance metrics endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.database.base import get_db
from app.database.models import ModelPerformance, Anomaly, TrafficLog
from app.models.schemas import ModelPerformanceResponse, ModelPerformanceListResponse
from app.utils.logger import get_logger
from datetime import datetime, timezone

logger = get_logger(__name__)
router = APIRouter(prefix="/api/model-metrics", tags=["model-metrics"])


@router.get("", response_model=ModelPerformanceListResponse)
async def get_model_metrics(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get model performance metrics history."""
    try:
        metrics = db.query(ModelPerformance).order_by(
            desc(ModelPerformance.evaluation_date)
        ).limit(limit).all()
        
        return ModelPerformanceListResponse(
            metrics=[ModelPerformanceResponse(
                id=m.id,
                model_version=m.model_version,
                evaluation_date=m.evaluation_date,
                total_predictions=m.total_predictions,
                true_positives=m.true_positives,
                false_positives=m.false_positives,
                true_negatives=m.true_negatives,
                false_negatives=m.false_negatives,
                precision=m.precision,
                recall=m.recall,
                f1_score=m.f1_score,
                accuracy=m.accuracy,
                auc_roc=m.auc_roc,
                avg_anomaly_score=m.avg_anomaly_score,
                threshold_used=m.threshold_used,
            ) for m in metrics],
            total=len(metrics)
        )
    except Exception as e:
        logger.error(f"Error fetching model metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching model metrics: {str(e)}")


@router.post("/evaluate")
async def evaluate_model_performance(
    limit: int = Query(None, ge=50, le=5000, description="Number of recent traffic logs to evaluate (defaults to config setting)"),
    db: Session = Depends(get_db)
):
    """
    Evaluate current model performance based on recent predictions.
    
    Uses the last N traffic logs (default: 500) to evaluate model performance.
    This ensures consistent, comparable metrics regardless of when data was generated.
    Perfect for demos where data might be sparse or old.
    """
    try:
        from app.config import settings
        
        # Use provided limit or default from config
        evaluation_limit = limit if limit is not None else settings.model_evaluation_logs
        
        logger.info(f"Evaluating model performance on last {evaluation_limit} traffic logs")
        
        # Get the most recent N traffic logs
        all_logs = db.query(TrafficLog).order_by(
            desc(TrafficLog.timestamp)
        ).limit(evaluation_limit).all()
        
        if not all_logs:
            raise HTTPException(
                status_code=404, 
                detail="No traffic logs found for evaluation"
            )
        
        # Get all anomaly log IDs from these traffic logs
        log_ids = [log.id for log in all_logs]
        anomalies_in_window = db.query(Anomaly).filter(
            Anomaly.traffic_log_id.in_(log_ids)
        ).all()
        
        # Create a set of traffic log IDs that have detected anomalies
        anomaly_log_ids = {a.traffic_log_id for a in anomalies_in_window if a.traffic_log_id}
        
        # Calculate metrics
        # True Positive: Anomaly detected AND actual anomaly (server error, very slow, or very large)
        # False Positive: Anomaly detected BUT no actual anomaly
        # True Negative: No anomaly detected AND no actual anomaly
        # False Negative: No anomaly detected BUT actual anomaly exists
        
        tp = 0
        fp = 0
        fn = 0
        tn = 0
        total_score = 0.0
        
        for log in all_logs:
            # Ground truth: consider multiple anomaly indicators
            # True anomaly if: server error (5xx), very slow response (>3000ms), or very large request (>10MB)
            is_true_anomaly = (
                log.status_code >= 500 or  # Server errors (5xx)
                log.response_time_ms > 3000 or  # Very slow (>3 seconds)
                (log.request_size_bytes and log.request_size_bytes > 10000000) or  # Very large request (>10MB)
                (log.response_size_bytes and log.response_size_bytes > 10000000)  # Very large response (>10MB)
            )
            
            # Check if this log was detected as an anomaly
            is_detected_anomaly = log.id in anomaly_log_ids
            
            if is_detected_anomaly:
                if is_true_anomaly:
                    tp += 1
                else:
                    fp += 1
                # Get anomaly score
                for anomaly in anomalies_in_window:
                    if anomaly.traffic_log_id == log.id:
                        total_score += anomaly.anomaly_score
                        break
            else:
                if is_true_anomaly:
                    fn += 1
                else:
                    tn += 1
        
        # Calculate metrics
        total = tp + fp + tn + fn
        if total == 0:
            raise HTTPException(status_code=400, detail="No data available for evaluation")
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / total if total > 0 else 0.0
        avg_score = total_score / (tp + fp) if (tp + fp) > 0 else 0.0
        
        # Save performance metrics
        model_perf = ModelPerformance(
            model_version="v1",
            evaluation_date=datetime.now(timezone.utc),
            total_predictions=total,
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            false_negatives=fn,
            precision=precision,
            recall=recall,
            f1_score=f1,
            accuracy=accuracy,
            avg_anomaly_score=avg_score,
            threshold_used=settings.anomaly_threshold
        )
        db.add(model_perf)
        db.commit()
        
        return ModelPerformanceResponse(
            id=model_perf.id,
            model_version=model_perf.model_version,
            evaluation_date=model_perf.evaluation_date,
            total_predictions=model_perf.total_predictions,
            true_positives=model_perf.true_positives,
            false_positives=model_perf.false_positives,
            true_negatives=model_perf.true_negatives,
            false_negatives=model_perf.false_negatives,
            precision=model_perf.precision,
            recall=model_perf.recall,
            f1_score=model_perf.f1_score,
            accuracy=model_perf.accuracy,
            auc_roc=model_perf.auc_roc,
            avg_anomaly_score=model_perf.avg_anomaly_score,
            threshold_used=model_perf.threshold_used,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating model performance: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error evaluating model: {str(e)}")

