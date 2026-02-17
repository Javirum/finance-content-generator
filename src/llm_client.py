from __future__ import annotations

import logging
import os
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv

from src.usage_tracker import record as _record_usage

load_dotenv()

DEFAULT_MODEL = "gpt-5.2"

logger = logging.getLogger(__name__)

# Pricing per 1M tokens (USD) — GPT-5.2, February 2026
PRICING = {
    "gpt-5.2": {"input": 1.75, "cached_input": 0.175, "output": 14.00},
}


def get_client() -> OpenAI:
    """Create and return an OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-key-here":
        raise RuntimeError(
            "OPENAI_API_KEY not set. Add your key to the .env file."
        )
    return OpenAI(api_key=api_key)


def _log_usage(response, model: str) -> Optional[dict]:
    """Log token usage and estimated cost from an API response."""
    usage = response.usage
    if usage is None:
        return None

    total_input = usage.prompt_tokens
    output = usage.completion_tokens
    cached = getattr(usage.prompt_tokens_details, "cached_tokens", 0) or 0
    uncached = total_input - cached

    prices = PRICING.get(model, PRICING["gpt-5.2"])
    cost_input = (uncached / 1_000_000) * prices["input"]
    cost_cached = (cached / 1_000_000) * prices["cached_input"]
    cost_output = (output / 1_000_000) * prices["output"]
    total_cost = cost_input + cost_cached + cost_output

    cache_pct = (cached / total_input * 100) if total_input else 0

    stats = {
        "input_tokens": total_input,
        "cached_tokens": cached,
        "uncached_tokens": uncached,
        "output_tokens": output,
        "cache_hit_pct": cache_pct,
        "cost_usd": total_cost,
    }

    logger.info(
        "Tokens: %d input (%d cached / %d new) + %d output | "
        "Cache hit: %.0f%% | Cost: $%.4f",
        total_input, cached, uncached, output, cache_pct, total_cost,
    )

    return stats


_last_usage_stats: Optional[dict] = None


def get_last_usage_stats() -> Optional[dict]:
    """Return the usage stats from the most recent generate() call."""
    return _last_usage_stats


def generate(client: OpenAI, messages: list[dict], model: str = DEFAULT_MODEL, temperature: float = 1) -> str:
    """Send messages to OpenAI and return the response text."""
    global _last_usage_stats

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        prompt_cache_retention="24h",
    )

    _last_usage_stats = _log_usage(response, model)
    if _last_usage_stats:
        _record_usage(_last_usage_stats)

    return response.choices[0].message.content.strip()
