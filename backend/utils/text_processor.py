"""Text cleaning, normalization, and language detection for code-mixed messages."""

import hashlib
import re
import unicodedata


# Devanagari Unicode range
_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
_LATIN_RE = re.compile(r"[a-zA-Z]")
_BENGALI_RE = re.compile(r"[\u0980-\u09FF]")
_GURMUKHI_RE = re.compile(r"[\u0A00-\u0A7F]")
_GUJARATI_RE = re.compile(r"[\u0A80-\u0AFF]")
_TAMIL_RE = re.compile(r"[\u0B80-\u0BFF]")
_TELUGU_RE = re.compile(r"[\u0C00-\u0C7F]")
_KANNADA_RE = re.compile(r"[\u0C80-\u0CFF]")
_MALAYALAM_RE = re.compile(r"[\u0D00-\u0D7F]")
_ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
_WHITESPACE_RE = re.compile(r"\s+")
_MAX_TEXT_LENGTH = 5000


def normalize(text: str) -> str:
    """Lowercase, strip, collapse whitespace, and normalize Unicode."""
    text = unicodedata.normalize("NFC", text)
    text = text.strip().lower()
    text = _WHITESPACE_RE.sub(" ", text)
    return text


def clean(text: str) -> str:
    """Remove control characters but keep Devanagari and standard punctuation."""
    cleaned = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat.startswith("C") and ch not in ("\n", "\t"):
            continue
        cleaned.append(ch)
    return "".join(cleaned)


def detect_language(text: str) -> str:
    """Return 'hindi', 'english', or 'mixed' based on script usage."""
    has_devanagari = bool(_DEVANAGARI_RE.search(text))
    has_latin = bool(_LATIN_RE.search(text))
    if has_devanagari and has_latin:
        return "mixed"
    if has_devanagari:
        return "hindi"
    return "english"


def detect_languages(text: str) -> list[str]:
    """Return a best-effort list of languages/scripts detected in text."""
    text = text or ""
    langs: list[str] = []

    if _LATIN_RE.search(text):
        langs.append("English")
    if _DEVANAGARI_RE.search(text):
        langs.append("Hindi")
    if _BENGALI_RE.search(text):
        langs.append("Bengali")
    if _GURMUKHI_RE.search(text):
        langs.append("Punjabi")
    if _GUJARATI_RE.search(text):
        langs.append("Gujarati")
    if _TAMIL_RE.search(text):
        langs.append("Tamil")
    if _TELUGU_RE.search(text):
        langs.append("Telugu")
    if _KANNADA_RE.search(text):
        langs.append("Kannada")
    if _MALAYALAM_RE.search(text):
        langs.append("Malayalam")
    if _ARABIC_RE.search(text):
        langs.append("Urdu")

    # De-duplicate while preserving order.
    seen = set()
    out: list[str] = []
    for lang in langs:
        if lang in seen:
            continue
        seen.add(lang)
        out.append(lang)
    return out or ["Unknown"]


def text_hash(text: str) -> str:
    """Generate a SHA-256 hex digest of the normalized text for cache keys."""
    normalized = normalize(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def validate_length(text: str) -> tuple[bool, str]:
    """Check that text is non-empty and within max length.

    Returns (is_valid, error_message).
    """
    if not text or not text.strip():
        return False, "Text is empty"
    if len(text) > _MAX_TEXT_LENGTH:
        return False, f"Text exceeds maximum length of {_MAX_TEXT_LENGTH} characters"
    return True, ""


def preprocess(text: str) -> str:
    """Full preprocessing pipeline: clean then normalize."""
    return normalize(clean(text))
