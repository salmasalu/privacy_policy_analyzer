from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.models import AnalysisRecord, PredictionLog, ErrorLog
from typing import Optional


def save_analysis(
    db: Session,
    input_type: str,
    risk_score: float,
    risk_label: str,
    summary: str,
    total_risky_clauses: int,
    top_risky_clauses: list,
    source_url: Optional[str] = None,
    filename: Optional[str] = None,
    processing_time_ms: Optional[float] = None,
    error_occurred: Optional[str] = None
) -> AnalysisRecord:
    record = AnalysisRecord(
        input_type=input_type,
        source_url=source_url,
        filename=filename,
        risk_score=risk_score,
        risk_label=risk_label,
        summary=summary,
        total_risky_clauses=total_risky_clauses,
        top_risky_clauses=top_risky_clauses,
        processing_time_ms=processing_time_ms,
        error_occurred=error_occurred
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_all_analyses(db: Session, limit: int = 50) -> list:
    return (
        db.query(AnalysisRecord)
        .order_by(desc(AnalysisRecord.created_at))
        .limit(limit)
        .all()
    )


def get_analysis_by_url(db: Session, url: str) -> Optional[AnalysisRecord]:
    return (
        db.query(AnalysisRecord)
        .filter(AnalysisRecord.source_url == url)
        .order_by(desc(AnalysisRecord.created_at))
        .first()
    )


def get_analysis_by_id(db: Session, analysis_id: int) -> Optional[AnalysisRecord]:
    return db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()


def log_predictions(db: Session, analysis_id: int, clauses: list):
    for clause in clauses:
        log = PredictionLog(
            analysis_id=analysis_id,
            clause_text=clause.get("clause", ""),
            predicted_risk_type=clause.get("risk_type", "unknown"),
            confidence=clause.get("confidence", 0.0),
            risk_level=clause.get("risk_level", "low")
        )
        db.add(log)
    db.commit()


def log_error(db: Session, endpoint: str, error_message: str, input_type: Optional[str] = None):
    error = ErrorLog(
        endpoint=endpoint,
        error_message=error_message,
        input_type=input_type
    )
    db.add(error)
    db.commit()


def get_analytics_summary(db: Session) -> dict:
    total = db.query(func.count(AnalysisRecord.id)).scalar()
    avg_score = db.query(func.avg(AnalysisRecord.risk_score)).scalar()
    avg_latency = db.query(func.avg(AnalysisRecord.processing_time_ms)).scalar()
    total_errors = db.query(func.count(ErrorLog.id)).scalar()

    by_input_type = (
        db.query(AnalysisRecord.input_type, func.count(AnalysisRecord.id))
        .group_by(AnalysisRecord.input_type)
        .all()
    )
    by_risk_label = (
        db.query(AnalysisRecord.risk_label, func.count(AnalysisRecord.id))
        .group_by(AnalysisRecord.risk_label)
        .all()
    )

    return {
        "total_analyses": total or 0,
        "avg_risk_score": round(avg_score, 2) if avg_score else 0.0,
        "avg_latency_ms": round(avg_latency, 2) if avg_latency else 0.0,
        "total_errors": total_errors or 0,
        "by_input_type": {row[0]: row[1] for row in by_input_type},
        "by_risk_label": {row[0]: row[1] for row in by_risk_label}
    }