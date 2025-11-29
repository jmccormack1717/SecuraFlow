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
    db: Session = Depends(get_db)
):
    """Evaluate current model performance based on recent predictions."""
    try:
        from app.config import settings
        
        # Get recent anomalies and traffic logs
        # For evaluation, we'll use a simple approach:
        # Compare detected anomalies with actual error patterns
        
        recent_anomalies = db.query(Anomaly).order_by(
            desc(Anomaly.detected_at)
        ).limit(1000).all()
        
        if not recent_anomalies:
            raise HTTPException(status_code=404, detail="No anomalies found for evaluation")
        
        # Get corresponding traffic logs
        traffic_log_ids = [a.traffic_log_id for a in recent_anomalies if a.traffic_log_id]
        traffic_logs = db.query(TrafficLog).filter(
            TrafficLog.id.in_(traffic_log_ids)
        ).all()
        
        # Create a mapping
        log_map = {log.id: log for log in traffic_logs}
        
        # Calculate metrics
        # True Positive: Anomaly detected AND actual error (status >= 400)
        # False Positive: Anomaly detected BUT no error (status < 400)
        # True Negative: No anomaly AND no error
        # False Negative: No anomaly BUT actual error
        
        tp = 0
        fp = 0
        fn = 0
        tn = 0
        total_score = 0.0
        
        anomaly_ids = {a.id for a in recent_anomalies}
        
        # Check all traffic logs in the time range
        start_time = min(a.detected_at for a in recent_anomalies)
        all_logs = db.query(TrafficLog).filter(
            TrafficLog.timestamp >= start_time
        ).limit(5000).all()
        
        for log in all_logs:
            # Better ground truth: consider multiple anomaly indicators
            # True anomaly if: server error (5xx), very slow response (>2000ms), or very large request (>10MB)
            is_true_anomaly = (
                log.status_code >= 500 or  # Server errors
                log.response_time_ms > 2000 or  # Very slow
                (log.request_size_bytes and log.request_size_bytes > 10000000) or  # Very large request
                (log.response_size_bytes and log.response_size_bytes > 50000000)  # Very large response
            )
            
            is_anomaly = any(a.traffic_log_id == log.id for a in recent_anomalies)
            
            if is_anomaly:
                if is_true_anomaly:
                    tp += 1
                else:
                    fp += 1
                # Get anomaly score
                for anomaly in recent_anomalies:
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

