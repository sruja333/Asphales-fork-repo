"""API route definitions for SurakshaAI Shield."""

import time
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.classifier import HybridClassifier
from context_engine import calculate_contextual_risk, extract_links, summarize_link_indicators
from explanation_engine import ExplanationEngine
from utils.logger import setup_logger
from utils.text_processor import detect_languages

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


def _count_scanned_blocks(text: str) -> int:
    blocks = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    return len(blocks) if blocks else 1


def _build_manipulation_radars(text: str, detected_signals: list[str]) -> list[str]:
    text_l = (text or "").lower()
    radars: list[str] = []

    if any("urgency" in s.lower() for s in detected_signals) or any(k in text_l for k in ("urgent", "immediately", "now", "final warning", "turant", "abhi")):
        radars.append("Urgency")
    if any("impersonation" in s.lower() for s in detected_signals) or any(k in text_l for k in ("bank", "rbi", "sbi", "hdfc", "icici", "support team", "security desk")):
        radars.append("Impersonation")
    if any("credential" in s.lower() for s in detected_signals) or any(k in text_l for k in ("otp", "password", "pin", "cvv", "kyc", "verify account", "netbanking", "mpin", "upi pin")):
        radars.append("Credential Harvesting")
    if any(k in text_l for k in ("block", "suspend", "freeze", "legal", "arrest", "warning")):
        radars.append("Fear/Threat Pressure")
    if any(k in text_l for k in ("fee", "pay", "payment", "refund", "subsidy", "claim", "prize", "lottery")):
        radars.append("Financial Enticement")
    if any(k in text_l for k in ("click", "link", "open", "visit", "tap here")):
        radars.append("Action Coercion")

    return sorted(set(radars))


def _build_technical_indicators(text: str, links: list[str], detected_signals: list[str]) -> tuple[list[str], list[str]]:
    summary = summarize_link_indicators(links)
    indicators = list(summary["technical_indicators"])
    suspicious_domains = summary["suspicious_domains"]
    text_l = (text or "").lower()

    if links:
        indicators.append("External link present")
    if any(k in text_l for k in ("otp", "password", "pin", "cvv", "aadhaar", "pan", "kyc", "netbanking", "mpin", "upi pin")):
        indicators.append("Sensitive information request pattern")
    if any("adjacent scam signals" in s.lower() for s in detected_signals):
        indicators.append("Stacked social engineering pattern")
    if any("impersonation" in s.lower() for s in detected_signals):
        indicators.append("Authority impersonation pattern")
    if any("urgency" in s.lower() for s in detected_signals):
        indicators.append("Urgency pressure pattern")

    return sorted(set(indicators)), suspicious_domains


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
    result_dict = result.to_dict()

    links = extract_links(request.text)
    ctx = calculate_contextual_risk(
        text=request.text,
        detected_features=[],
        links=links,
        base_score=float(result_dict.get("overall_risk", 0)) / 100.0,
    )
    technical_indicators, suspicious_domains = _build_technical_indicators(request.text, links, ctx["detected_signals"])
    manipulation_radars = _build_manipulation_radars(request.text, ctx["detected_signals"])

    result_dict.update(
        {
            "threat_score": result_dict.get("overall_risk", 0),
            "context_impact": int(round(float(ctx.get("context_boost", 0.0)) * 100)),
            "scanned_blocks": _count_scanned_blocks(request.text),
            "detected_language": ", ".join(detect_languages(request.text)),
            "manipulation_radars": manipulation_radars,
            "technical_indicators": technical_indicators,
            "suspicious_domains": suspicious_domains,
        }
    )
    return result_dict


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
    technical_indicators, suspicious_domains = _build_technical_indicators(request.text, links, ctx["detected_signals"])
    manipulation_radars = _build_manipulation_radars(request.text, ctx["detected_signals"])

    return {
        "risk_score": ctx["risk_score"],
        "risk_level": ctx["risk_level"],
        "threat_score": int(round(ctx["risk_score"] * 100)),
        "context_impact": int(round(ctx["context_boost"] * 100)),
        "scanned_blocks": _count_scanned_blocks(request.text),
        "detected_language": ", ".join(detect_languages(request.text)),
        "manipulation_radars": manipulation_radars,
        "technical_indicators": technical_indicators,
        "suspicious_domains": suspicious_domains,
        "detected_signals": ctx["detected_signals"],
        "context_boost": ctx["context_boost"],
        "ml": {"risk_score": base_prob, "is_phishing": base_prob >= 0.5},
        "links": links,
        "genai_validation": exp.get("validation", {}),
        "structured_explanation": exp.get("explanation", {}),
    }
