from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    input_type = Column(String(20), nullable=False)       # url | pdf | text
    source_url = Column(Text, nullable=True)
    filename = Column(String(255), nullable=True)
    risk_score = Column(Float, nullable=False)
    risk_label = Column(String(50), nullable=False)
    summary = Column(Text, nullable=False)
    total_risky_clauses = Column(Integer, nullable=False)
    top_risky_clauses = Column(JSON, nullable=False)
    processing_time_ms = Column(Float, nullable=True)
    error_occurred = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, nullable=False)
    clause_text = Column(Text, nullable=False)
    predicted_risk_type = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    input_type = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())