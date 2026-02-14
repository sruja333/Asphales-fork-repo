"""Context-aware risk scoring for phishing detection."""

from __future__ import annotations

import re
from urllib.parse import urlparse
from typing import Any

URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
IP_URL_RE = re.compile(r"https?://(?:\d{1,3}\.){3}\d{1,3}(?:[:/]\S*)?", re.IGNORECASE)
SHORTENER_RE = re.compile(r"https?://(?:bit\.ly|tinyurl\.com|t\.co|goo\.gl)/\S+", re.IGNORECASE)
SUSPICIOUS_TLD_RE = re.compile(r"https?://[^\s]+\.(?:top|xyz|click|gq|tk|work|fit)(?:/|$)", re.IGNORECASE)

URGENCY_TERMS = {"urgent", "immediately", "now", "final warning", "तुरंत", "இப்போது", "এখনই", "urg3nt"}
IMPERSONATION_TERMS = {"bank", "rbi", "sbi", "hdfc", "icici", "support team", "security desk"}
CREDENTIAL_TERMS = {"otp", "password", "pin", "cvv", "credential", "verify account", "kyc"}
SAFE_TLDS = {"com", "in"}


def classify_risk_level(score: float) -> str:
    if score <= 0.30:
        return "SAFE"
    if score <= 0.55:
        return "SUSPICIOUS"
    if score <= 0.80:
        return "HIGH RISK"
    return "CRITICAL"


def extract_links(text: str) -> list[str]:
    return URL_RE.findall(text or "")


def _has_any(text_l: str, terms: set[str]) -> bool:
    return any(t in text_l for t in terms)


def _domain_and_tld(url: str) -> tuple[str, str]:
    try:
        host = (urlparse(url).hostname or "").lower().strip(".")
    except Exception:
        return "", ""
    if not host:
        return "", ""
    parts = host.split(".")
    return host, parts[-1] if parts else ""


def _is_suspicious_domain(url: str) -> bool:
    host, tld = _domain_and_tld(url)
    if not host:
        return False
    if re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", host):
        return True
    if tld and tld not in SAFE_TLDS:
        return True
    return False


def summarize_link_indicators(links: list[str]) -> dict[str, Any]:
    suspicious_domains: list[str] = []
    indicators: list[str] = []

    has_ip_url = any(IP_URL_RE.search(l) for l in links)
    has_shortener = any(SHORTENER_RE.search(l) for l in links)
    has_unusual_tld = any(SUSPICIOUS_TLD_RE.search(l) or _is_suspicious_domain(l) for l in links)

    for link in links:
        host, _ = _domain_and_tld(link)
        if host and _is_suspicious_domain(link):
            suspicious_domains.append(host)

    if has_ip_url:
        indicators.append("IP-based URL")
    if has_shortener:
        indicators.append("Shortened URL")
    if has_unusual_tld:
        indicators.append("Uncommon or suspicious top-level domain")
    if suspicious_domains:
        indicators.append("Suspicious website domain")

    return {
        "suspicious_domains": sorted(set(suspicious_domains)),
        "technical_indicators": indicators,
    }


def calculate_contextual_risk(text: str, detected_features: list[str] | None, links: list[str] | None, base_score: float = 0.0) -> dict[str, Any]:
    text = text or ""
    text_l = text.lower()
    links = links or extract_links(text)
    detected_features = detected_features or []

    boosts = 0.0
    signals: list[str] = list(detected_features)

    urgency = _has_any(text_l, URGENCY_TERMS)
    impersonation = _has_any(text_l, IMPERSONATION_TERMS)
    credential_req = _has_any(text_l, CREDENTIAL_TERMS)

    suspicious_url = any(
        IP_URL_RE.search(l)
        or SHORTENER_RE.search(l)
        or SUSPICIOUS_TLD_RE.search(l)
        or _is_suspicious_domain(l)
        for l in links
    )

    if urgency and links:
        boosts += 0.08
        signals.append("Urgency with link")

    if impersonation and credential_req:
        boosts += 0.12
        signals.append("Impersonation + credential request")

    if suspicious_url:
        boosts += 0.10
        signals.append("Suspicious URL structure")

    sentences = [s.strip() for s in re.split(r"[.!?\n]+", text_l) if s.strip()]
    for i in range(len(sentences) - 1):
        a, b = sentences[i], sentences[i + 1]
        if (_has_any(a, URGENCY_TERMS) and _has_any(b, CREDENTIAL_TERMS)) or (
            _has_any(a, IMPERSONATION_TERMS) and _has_any(b, CREDENTIAL_TERMS)
        ):
            boosts += 0.07
            signals.append("Adjacent scam signals")
            break

    final = max(0.0, min(1.0, base_score + boosts))
    return {
        "risk_score": round(final, 4),
        "risk_level": classify_risk_level(final),
        "detected_signals": sorted(set(signals)),
        "context_boost": round(boosts, 4),
    }
