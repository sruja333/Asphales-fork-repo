"""API route definitions for SurakshaAI Shield."""

import time
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.classifier import HybridClassifier
from context_engine import calculate_contextual_risk, extract_links
from explanation_engine import ExplanationEngine
from utils.logger import setup_logger

logger = setup_logger("api")

router = APIRouter()
classifier: Optional[HybridClassifier] = None
_start_time: float = time.time()
explainer = ExplanationEngine()


def set_classifier(c: HybridClassifier) -> None:
    global classifier
    classifier = c


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


class BatchAnalyzeRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=50)


@router.get("/")
async def health_check():
    uptime = time.time() - _start_time
    return {
        "status": "ok",
        "service": "SurakshaAI Shield",
        "version": "1.0.0",
        "uptime_seconds": round(uptime, 1),
        "genai_available": classifier.genai.is_available() if classifier else False,
    }


@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    if classifier is None:
        raise HTTPException(status_code=503, detail="Classifier not initialized")
    result = await classifier.classify(request.text)
    return result.to_dict()


@router.post("/batch-analyze")
async def batch_analyze(request: BatchAnalyzeRequest):
    if classifier is None:
        raise HTTPException(status_code=503, detail="Classifier not initialized")
    results = await classifier.batch_classify(request.texts)
    return {"results": [r.to_dict() for r in results], "count": len(results)}


@router.get("/stats")
async def stats():
    if classifier is None:
        raise HTTPException(status_code=503, detail="Classifier not initialized")
    return classifier.get_stats()


@router.get("/patterns")
async def patterns():
    """Deprecated route retained for compatibility."""
    return {
        "deprecated": True,
        "message": "Pattern matching removed. Use /stats for ML model information.",
        "total_patterns": 0,
    }


@router.post("/analyze_text")
async def analyze_text(request: AnalyzeRequest):
    if classifier is None:
        raise HTTPException(status_code=503, detail="Classifier not initialized")

    ml = classifier.ml.predict(request.text)
    base_prob = float(ml.get("confidence", 0.0))
    links = extract_links(request.text)
    ctx = calculate_contextual_risk(
        text=request.text,
        detected_features=[],
        links=links,
        base_score=base_prob,
    )
    exp = explainer.validate(
        text=request.text,
        ml_result={"risk_score": base_prob, "is_phishing": base_prob >= 0.5},
        detected_features=ctx["detected_signals"],
        links=links,
        context_result=ctx,
    )

    return {
        "risk_score": ctx["risk_score"],
        "risk_level": ctx["risk_level"],
        "detected_signals": ctx["detected_signals"],
        "context_boost": ctx["context_boost"],
        "ml": {"risk_score": base_prob, "is_phishing": base_prob >= 0.5},
        "links": links,
        "genai_validation": exp.get("validation", {}),
        "structured_explanation": exp.get("explanation", {}),
    }
