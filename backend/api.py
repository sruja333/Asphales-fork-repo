"""FastAPI service for ML + contextual + GenAI phishing analysis."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from context_engine import calculate_contextual_risk, extract_links
from explanation_engine import ExplanationEngine
from train_model import AdvancedPhishingModel

MODEL_PATH = Path("models/advanced/phishing_model.json")


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


class InferenceEngine:
    def __init__(self, model_path: Path):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. Run dataset_builder.py and train_model.py first."
            )
        self.model = AdvancedPhishingModel.load(model_path)

    def predict(self, text: str) -> dict:
        prob = float(self.model.predict_proba(text))
        return {
            "risk_score": prob,
            "is_phishing": prob >= self.model.threshold,
            "threshold": self.model.threshold,
        }


app = FastAPI(title="SurakshaAI Advanced Detector", version="2.0.0")
engine: InferenceEngine | None = None
explainer = ExplanationEngine()


@app.on_event("startup")
def startup() -> None:
    global engine
    engine = InferenceEngine(MODEL_PATH)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": engine is not None}


@app.post("/analyze_text")
def analyze_text(request: AnalyzeRequest) -> dict:
    if engine is None:
        raise HTTPException(status_code=503, detail="Model not initialized")

    text = request.text
    links = extract_links(text)

    detected_features: list[str] = []
    ml_result = engine.predict(text)
    ctx = calculate_contextual_risk(
        text=text,
        detected_features=detected_features,
        links=links,
        base_score=ml_result["risk_score"],
    )

    explanation = explainer.validate(
        text=text,
        ml_result=ml_result,
        detected_features=ctx["detected_signals"],
        links=links,
        context_result=ctx,
    )

    return {
        "risk_score": ctx["risk_score"],
        "risk_level": ctx["risk_level"],
        "detected_signals": ctx["detected_signals"],
        "context_boost": ctx["context_boost"],
        "ml": ml_result,
        "links": links,
        "genai_validation": explanation.get("validation", {}),
        "structured_explanation": explanation.get("explanation", {}),
    }
