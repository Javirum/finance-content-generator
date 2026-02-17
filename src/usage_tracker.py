"""Tracks cumulative API token usage and cost, persisted to a JSON file."""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Optional

USAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "usage")
USAGE_FILE = os.path.join(USAGE_DIR, "usage_log.json")


def _load_log() -> list:
    if not os.path.exists(USAGE_FILE):
        return []
    with open(USAGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_log(entries: list) -> None:
    os.makedirs(USAGE_DIR, exist_ok=True)
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


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
