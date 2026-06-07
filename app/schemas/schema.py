from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# INPUT MODELS

class URLInput(BaseModel):
    url: str

class TextInput(BaseModel):
    text: str


# CLAUSE RESPONSE

class ClauseResult(BaseModel):
    clause: str
    risk_type: str
    confidence: float
    explanation: str
    risk_level: str                  # high | medium | low


# ANALYSIS RESPONSE

class AnalysisResponse(BaseModel):
    risk_score: float                # 0–10
    risk_label: str                  # LOW RISK | MEDIUM RISK | HIGH RISK
    summary: str
    top_risky_clauses: List[ClauseResult]
    total_risky_clauses: int
    processing_time_ms: float
    cached: bool = False             # True if returned from DB cache


# HISTORY RESPONSE

class HistoryRecord(BaseModel):
    id: int
    input_type: str                  # url | pdf | text
    source_url: Optional[str]
    filename: Optional[str]
    risk_score: float
    risk_label: str
    total_risky_clauses: int
    processing_time_ms: Optional[float]
    created_at: Optional[str]


# ANALYTICS RESPONSE

class AnalyticsSummary(BaseModel):
    total_analyses: int
    avg_risk_score: float
    avg_latency_ms: float
    total_errors: int
    by_input_type: dict              # {"url": 10, "pdf": 3, "text": 7}
    by_risk_label: dict              # {"HIGH RISK": 5, "MEDIUM RISK": 8, ...}