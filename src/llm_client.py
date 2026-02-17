from __future__ import annotations

import logging
import os
from datetime import datetime
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
    "gpt-4o-mini-tts": {"input": 0.60, "output": 12.00},
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


PODCASTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "podcasts")

TTS_VOICE_INSTRUCTIONS = (
    "Speak like a podcast host roasting the listener's financial habits. "
    "Energetic, funny, slightly sarcastic."
)


def generate_speech(client: OpenAI, text: str, topic: str, voice: str = "coral") -> str:
    """Convert *text* to speech using OpenAI TTS and save as MP3. Returns file path."""
    os.makedirs(PODCASTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    slug = topic.lower().replace(" ", "-")[:30]
    filepath = os.path.join(PODCASTS_DIR, f"{timestamp}_{slug}.mp3")

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
        instructions=TTS_VOICE_INSTRUCTIONS,
    ) as response:
        response.stream_to_file(filepath)

    # Rough cost estimate for TTS (input text tokens + audio output tokens)
    # Input: ~1 token per 4 chars; Audio output: ~1 token per char of input text
    input_tokens = len(text) // 4
    audio_output_tokens = len(text)
    prices = PRICING["gpt-4o-mini-tts"]
    cost = (input_tokens / 1_000_000) * prices["input"] + (audio_output_tokens / 1_000_000) * prices["output"]

    stats = {
        "input_tokens": input_tokens,
        "cached_tokens": 0,
        "uncached_tokens": input_tokens,
        "output_tokens": audio_output_tokens,
        "cache_hit_pct": 0,
        "cost_usd": cost,
    }
    _record_usage(stats)
    logger.info("TTS generated: %s | Est. cost: $%.4f", filepath, cost)

    return filepath
