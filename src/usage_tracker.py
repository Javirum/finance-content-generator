"""Tracks cumulative API token usage and cost, persisted to a JSON file."""
from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import datetime
from typing import Optional

from src.config import USAGE_DIR, USAGE_FILE

logger = logging.getLogger(__name__)


def _load_log() -> list:
    if not USAGE_FILE.exists():
        return []
    try:
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not read usage log, starting fresh: %s", e)
        return []


def _save_log(entries: list) -> None:
    USAGE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        # Atomic write: write to temp file then rename
        fd, tmp_path = tempfile.mkstemp(dir=USAGE_DIR, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
        os.replace(tmp_path, USAGE_FILE)
    except OSError as e:
        logger.warning("Failed to save usage log: %s", e)
        # Clean up temp file if rename failed
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def record(stats: dict) -> None:
    """Append a usage entry with a timestamp."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        **stats,
    }
    entries = _load_log()
    entries.append(entry)
    _save_log(entries)


def get_monthly_summary(year: Optional[int] = None, month: Optional[int] = None) -> dict:
    """Return aggregated usage for a given month (defaults to current month)."""
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    prefix = f"{year}-{month:02d}"

    entries = _load_log()
    monthly = [e for e in entries if e.get("timestamp", "").startswith(prefix)]

    total_input = sum(e.get("input_tokens", 0) for e in monthly)
    total_cached = sum(e.get("cached_tokens", 0) for e in monthly)
    total_output = sum(e.get("output_tokens", 0) for e in monthly)
    total_cost = sum(e.get("cost_usd", 0) for e in monthly)
    request_count = len(monthly)
    avg_cache_pct = (
        sum(e.get("cache_hit_pct", 0) for e in monthly) / request_count
        if request_count
        else 0
    )

    return {
        "month": prefix,
        "requests": request_count,
        "input_tokens": total_input,
        "cached_tokens": total_cached,
        "output_tokens": total_output,
        "total_tokens": total_input + total_output,
        "avg_cache_hit_pct": avg_cache_pct,
        "total_cost_usd": total_cost,
    }
