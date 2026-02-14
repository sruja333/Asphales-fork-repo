"""Pure-Python TF-IDF + Logistic Regression phishing classifier."""

from __future__ import annotations

import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from utils.logger import setup_logger

logger = setup_logger("ml_classifier")

BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = BASE_DIR / "data" / "combined_training.csv"
MODEL_PATH = BASE_DIR / "models" / "phishing_tfidf_logreg_model.json"
TOKEN_RE = re.compile(r"\w+", re.UNICODE)
MULTISPACE_RE = re.compile(r"\s+")


class MLPhishingClassifier:
    """TF-IDF + logistic regression implemented without external ML libs."""

    def __init__(self):
        self.model_name = "tfidf-logistic-regression"
        self.model: dict = {}
        self._load_or_train()

    def _load_or_train(self) -> None:
        if MODEL_PATH.exists():
            self.model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
            logger.info("Loaded ML model from %s", MODEL_PATH)
            return
        logger.warning("ML model missing, training from dataset...")
        self.train(DATASET_PATH, MODEL_PATH)

    def _tokens(self, text: str) -> list[str]:
        return TOKEN_RE.findall(self._normalize(text))

    def _normalize(self, text: str) -> str:
        text = (text or "").replace("\x00", " ").lower()
        return MULTISPACE_RE.sub(" ", text).strip()

    def _word_ngrams(self, tokens: list[str]) -> list[str]:
        grams = list(tokens)
        grams.extend(f"{tokens[i]} {tokens[i + 1]}" for i in range(len(tokens) - 1))
        return grams

    def _char_ngrams(self, text: str, min_n: int = 3, max_n: int = 5) -> list[str]:
        normalized = self._normalize(text)
        grams: list[str] = []
        for n in range(min_n, max_n + 1):
            grams.extend(normalized[i : i + n] for i in range(max(0, len(normalized) - n + 1)))
        return grams

    def _features(self, text: str) -> list[str]:
        tokens = self._tokens(text)
        return self._word_ngrams(tokens) + self._char_ngrams(text)

    def _build_vocab_and_idf(
        self, docs_features: list[list[str]], max_features: int = 30000, min_df: int = 2
    ) -> tuple[dict[str, int], dict[int, float]]:
        df = Counter()
        tf_global = Counter()
        for feats in docs_features:
            tf_global.update(feats)
            df.update(set(feats))

        candidates = [(term, freq) for term, freq in tf_global.items() if df[term] >= min_df]
        top_terms = [term for term, _ in sorted(candidates, key=lambda x: x[1], reverse=True)[:max_features]]
        vocab = {t: i for i, t in enumerate(top_terms)}

        n_docs = len(docs_features)
        idf: dict[int, float] = {}
        for term, idx in vocab.items():
            idf[idx] = math.log((1 + n_docs) / (1 + df[term])) + 1.0
        return vocab, idf

    def _vectorize(self, feats: list[str], vocab: dict[str, int], idf: dict[int, float]) -> dict[int, float]:
        counts = Counter(t for t in feats if t in vocab)
        if not counts:
            return {}
        total = sum(counts.values())
        vec = {}
        for term, c in counts.items():
            idx = vocab[term]
            tf = c / total
            vec[idx] = tf * idf[idx]
        norm = math.sqrt(sum(v * v for v in vec.values()))
        if norm > 0:
            for k in list(vec.keys()):
                vec[k] /= norm
        return vec

    def train(self, dataset_path: Path, model_path: Path) -> None:
        labels: list[int] = []
        docs_features: list[list[str]] = []

        with dataset_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row["text"]
                label = int(row["label"])
                feats = self._features(text)
                labels.append(label)
                docs_features.append(feats)

        vocab, idf = self._build_vocab_and_idf(docs_features)
        vectors = [self._vectorize(feats, vocab, idf) for feats in docs_features]

        weights = defaultdict(float)
        bias = 0.0
        lr = 0.22
        reg = 1e-5
        epochs = 16

        idxs = list(range(len(vectors)))
        random.seed(42)

        pos = sum(labels)
        neg = len(labels) - pos
        w_pos = len(labels) / (2 * pos) if pos else 1.0
        w_neg = len(labels) / (2 * neg) if neg else 1.0

        for _ in range(epochs):
            random.shuffle(idxs)
            for i in idxs:
                x = vectors[i]
                y = labels[i]
                z = bias + sum(weights[j] * v for j, v in x.items())
                p = 1.0 / (1.0 + math.exp(-max(-30, min(30, z))))
                class_weight = w_pos if y == 1 else w_neg
                err = (p - y) * class_weight

                for j, v in x.items():
                    weights[j] -= lr * (err * v + reg * weights[j])
                bias -= lr * err

            lr *= 0.9

        model = {
            "model": self.model_name,
            "vocab": vocab,
            "idf": {str(k): v for k, v in idf.items()},
            "weights": {str(k): w for k, w in weights.items()},
            "bias": bias,
        }

        model_path.parent.mkdir(parents=True, exist_ok=True)
        model_path.write_text(json.dumps(model, ensure_ascii=False), encoding="utf-8")
        self.model = model
        logger.info("Trained and saved ML model to %s", model_path)

    def predict(self, text: str) -> dict:
        if not self.model:
            return {"risk_score": 0, "is_phishing": False, "confidence": 0.0, "model": self.model_name}

        vocab = self.model["vocab"]
        idf = {int(k): float(v) for k, v in self.model["idf"].items()}
        weights = {int(k): float(v) for k, v in self.model["weights"].items()}
        bias = float(self.model["bias"])

        x = self._vectorize(self._features(text), vocab, idf)
        z = bias + sum(weights.get(i, 0.0) * v for i, v in x.items())
        prob = 1.0 / (1.0 + math.exp(-max(-30, min(30, z))))
        risk = int(round(prob * 100))

        return {
            "risk_score": risk,
            "is_phishing": prob >= 0.5,
            "confidence": prob,
            "model": self.model_name,
        }

    def get_info(self) -> dict:
        return {
            "model": self.model_name,
            "model_path": str(MODEL_PATH),
            "dataset_path": str(DATASET_PATH),
            "dataset_exists": DATASET_PATH.exists(),
            "model_exists": MODEL_PATH.exists(),
        }
