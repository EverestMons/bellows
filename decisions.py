"""Intermediate decision detection via phrase-grep on assistant-event text blocks."""

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger("bellows")


def resolve_governance_root() -> Path:
    """Walk up from this file to the nearest ancestor containing COMPANY.md (governance root)."""
    current = Path(__file__).resolve().parent
    while True:
        if (current / "COMPANY.md").exists():
            return current
        parent = current.parent
        if parent == current:
            # Filesystem root reached — fall back to legacy two-parent assumption
            logger.warning("decisions: COMPANY.md marker not found; falling back to __file__.parent.parent")
            return Path(__file__).resolve().parent.parent
        current = parent


GOVERNANCE_ROOT = resolve_governance_root()
PHRASES_FILE = GOVERNANCE_ROOT / "INTERMEDIATE_DECISION_PHRASES.md"

_cached_phrases = None


def load_phrases() -> list:
    """Read INTERMEDIATE_DECISION_PHRASES.md, parse bullet lines, return lowercased phrase list.

    Slash-separated alternatives on a single line are split into individual phrases.
    Result is cached at module level after first call.
    """
    global _cached_phrases
    if _cached_phrases is not None:
        return _cached_phrases

    if not PHRASES_FILE.exists():
        logger.warning("decisions: phrase file not found at %s", PHRASES_FILE)
        _cached_phrases = []
        return _cached_phrases

    phrases = []
    text = PHRASES_FILE.read_text()
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        entry = line[2:].strip()
        if not entry:
            continue
        # Split slash-separated alternatives
        parts = [p.strip() for p in entry.split(" / ")]
        for part in parts:
            # Strip trailing parenthetical notes like "(followed by ...)"
            part = re.sub(r'\s*\(.*?\)\s*$', '', part)
            if part:
                phrases.append(part.lower())

    _cached_phrases = phrases
    return _cached_phrases


def extract_decision_blocks(raw_output, phrases: list) -> list:
    """Scan NDJSON stream for assistant text blocks matching decision phrases.

    Args:
        raw_output: Either a string (NDJSON stream) or a pre-parsed list of event dicts.
        phrases: Lowercased phrase list from load_phrases().

    Returns:
        List of dicts: {"event_idx": int, "text": str, "matched_phrases": list[str]}
        for each assistant text block matching at least one phrase.
        Text is truncated to 500 chars.
    """
    if not raw_output or not phrases:
        return []

    # Parse NDJSON if string
    if isinstance(raw_output, str):
        events = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if isinstance(event, dict):
                    events.append(event)
            except (json.JSONDecodeError, ValueError):
                continue
    elif isinstance(raw_output, list):
        events = raw_output
    else:
        return []

    results = []
    for idx, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        if event.get("type") != "assistant":
            continue

        # Extract text from content items
        content = event.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue

        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "text":
                continue
            text = item.get("text", "")
            if not text:
                continue

            text_lower = text.lower()
            matched = [p for p in phrases if p in text_lower]
            if matched:
                results.append({
                    "event_idx": idx,
                    "text": text[:500],
                    "matched_phrases": matched,
                })

    return results
