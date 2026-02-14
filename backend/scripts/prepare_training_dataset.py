"""Build a unified training CSV (text,label) from all dataset sources."""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
OUT_PATH = BACKEND / "data" / "combined_training.csv"

STANDARD_SOURCES = [
    ROOT / "phishing_multilingual_7500.csv",
    BACKEND / "data" / "phishing_multilingual_7500.csv",
]
RAW_SOURCE = ROOT / "Dataset of training (Threats and safe messages) (15 languages).csv"

SAFE_MARKERS = ("safe",)
THREAT_MARKERS = ("threat", "fraud", "phishing", "unsafe", "scam")


def _clean_text(text: str) -> str:
    text = (text or "").replace("\x00", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_standard_csv(path: Path) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "text" not in reader.fieldnames or "label" not in reader.fieldnames:
            return rows
        for row in reader:
            text = _clean_text(row.get("text", ""))
            if not text:
                continue
            try:
                label = int(str(row.get("label", "")).strip())
            except ValueError:
                continue
            if label not in (0, 1):
                continue
            rows.append((text, label))
    return rows


def load_raw_export(path: Path) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    if not path.exists():
        return rows

    content = path.read_text(encoding="utf-8", errors="replace")
    current_label: int | None = None

    for line in content.splitlines():
        line_l = line.lower()
        if any(m in line_l for m in SAFE_MARKERS):
            current_label = 0
        if any(m in line_l for m in THREAT_MARKERS):
            current_label = 1

        if current_label is None:
            continue

        # Handles patterns like ""message"" seen in exported file.
        candidates = re.findall(r'""([^"]+?)""', line)
        if not candidates:
            continue

        for c in candidates:
            text = _clean_text(c)
            if len(text) < 5:
                continue
            rows.append((text, current_label))

    return rows


def dedupe(rows: list[tuple[str, int]]) -> list[tuple[str, int]]:
    seen: set[tuple[str, int]] = set()
    out: list[tuple[str, int]] = []
    for text, label in rows:
        key = (text.lower(), label)
        if key in seen:
            continue
        seen.add(key)
        out.append((text, label))
    return out


def main() -> None:
    combined: list[tuple[str, int]] = []

    for src in STANDARD_SOURCES:
        rows = load_standard_csv(src)
        combined.extend(rows)
        print(f"[source] {src} -> {len(rows)} rows")

    raw_rows = load_raw_export(RAW_SOURCE)
    combined.extend(raw_rows)
    print(f"[source] {RAW_SOURCE} -> {len(raw_rows)} rows")

    combined = dedupe(combined)
    pos = sum(1 for _, y in combined if y == 1)
    neg = len(combined) - pos

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        writer.writerows(combined)

    print(f"[output] {OUT_PATH} -> {len(combined)} rows (phishing={pos}, safe={neg})")


if __name__ == "__main__":
    main()
