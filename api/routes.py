from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.core.extractor import extract_text_from_url, extract_text_from_pdf
from app.core.pipeline import run_pipeline
from app.db.database import get_db
from app.db import crud

router = APIRouter()

# INPUT MODELS

class URLInput(BaseModel):
    url: str

class TextInput(BaseModel):
    text: str

# ENDPOINTS

@router.post("/analyze-url")
def analyze_url(
    input: URLInput,
    top_n: Optional[int] = 5,
    db: Session = Depends(get_db)
):
    # Cache check — skip reprocessing same URL
    existing = crud.get_analysis_by_url(db, input.url)
    if existing:
        return {
            "risk_score": existing.risk_score,
            "risk_label": existing.risk_label,
            "summary": existing.summary,
            "top_risky_clauses": existing.top_risky_clauses,
            "total_risky_clauses": existing.total_risky_clauses,
            "processing_time_ms": existing.processing_time_ms,
            "cached": True
        }

    try:
        text = extract_text_from_url(input.url)
        if text.lower().startswith("error"):
            raise HTTPException(status_code=400, detail=text)

        result = run_pipeline(text, top_n=top_n)

        record = crud.save_analysis(
            db=db,
            input_type="url",
            source_url=input.url,
            risk_score=result["risk_score"],
            risk_label=result["risk_label"],
            summary=result["summary"],
            total_risky_clauses=result["total_risky_clauses"],
            top_risky_clauses=result["top_risky_clauses"],
            processing_time_ms=result["processing_time_ms"]
        )

        crud.log_predictions(db, record.id, result["top_risky_clauses"])

        result["cached"] = False
        return result

    except HTTPException:
        raise
    except Exception as e:
        crud.log_error(db, endpoint="/analyze-url", error_message=str(e), input_type="url")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-text")
def analyze_text(
    input: TextInput,
    top_n: Optional[int] = 5,
    db: Session = Depends(get_db)
):
    if not input.text.strip():
        raise HTTPException(status_code=400, detail="No text provided")

    try:
        result = run_pipeline(input.text, top_n=top_n)

        record = crud.save_analysis(
            db=db,
            input_type="text",
            risk_score=result["risk_score"],
            risk_label=result["risk_label"],
            summary=result["summary"],
            total_risky_clauses=result["total_risky_clauses"],
            top_risky_clauses=result["top_risky_clauses"],
            processing_time_ms=result["processing_time_ms"]
        )

        crud.log_predictions(db, record.id, result["top_risky_clauses"])

        result["cached"] = False
        return result

    except HTTPException:
        raise
    except Exception as e:
        crud.log_error(db, endpoint="/analyze-text", error_message=str(e), input_type="text")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-pdf")
def analyze_pdf(
    file: UploadFile = File(...),
    top_n: Optional[int] = 5,
    db: Session = Depends(get_db)
):
    try:
        text = extract_text_from_pdf(file.file)
        if text.lower().startswith("error"):
            raise HTTPException(status_code=400, detail=text)

        result = run_pipeline(text, top_n=top_n)

        record = crud.save_analysis(
            db=db,
            input_type="pdf",
            filename=file.filename,
            risk_score=result["risk_score"],
            risk_label=result["risk_label"],
            summary=result["summary"],
            total_risky_clauses=result["total_risky_clauses"],
            top_risky_clauses=result["top_risky_clauses"],
            processing_time_ms=result["processing_time_ms"]
        )

        crud.log_predictions(db, record.id, result["top_risky_clauses"])

        result["cached"] = False
        return result

    except HTTPException:
        raise
    except Exception as e:
        crud.log_error(db, endpoint="/analyze-pdf", error_message=str(e), input_type="pdf")
        raise HTTPException(status_code=500, detail=str(e))

# HISTORY + ANALYTICS ENDPOINTS

@router.get("/history")
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    """Returns last N analyses — powers history tab in Streamlit."""
    records = crud.get_all_analyses(db, limit=limit)
    return [
        {
            "id": r.id,
            "input_type": r.input_type,
            "source_url": r.source_url,
            "filename": r.filename,
            "risk_score": r.risk_score,
            "risk_label": r.risk_label,
            "total_risky_clauses": r.total_risky_clauses,
            "processing_time_ms": r.processing_time_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """Returns usage stats — powers monitoring dashboard in Streamlit."""
    return crud.get_analytics_summary(db)