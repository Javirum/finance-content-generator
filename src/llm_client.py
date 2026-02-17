from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from typing import Optional

import openai
from openai import OpenAI
from dotenv import load_dotenv

from src.config import DEFAULT_MODEL, PRICING, PODCASTS_DIR
from src.usage_tracker import record as _record_usage

load_dotenv()

logger = logging.getLogger(__name__)


def get_client(api_key: str | None = None) -> OpenAI:
    """Create and return an OpenAI client.

    Checks for a key in this order: explicit argument → st.secrets → env var.
    """
    if not api_key:
        # Try Streamlit secrets (used on Streamlit Cloud)
        try:
            import streamlit as st
            api_key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            pass
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-key-here":
        raise RuntimeError(
            "OPENAI_API_KEY not set. Add your key to .env, Streamlit secrets, or pass it directly."
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

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            prompt_cache_retention="24h",
        )
    except openai.RateLimitError:
        logger.warning("Rate limited, retrying in 5s...")
        time.sleep(5)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            prompt_cache_retention="24h",
        )
    except openai.APIConnectionError as e:
        raise RuntimeError(f"Could not connect to OpenAI API: {e}") from e
    except openai.APIError as e:
        raise RuntimeError(f"OpenAI API error: {e}") from e

    _last_usage_stats = _log_usage(response, model)
    if _last_usage_stats:
        _record_usage(_last_usage_stats)

    return response.choices[0].message.content.strip()


TTS_VOICE_INSTRUCTIONS = (
    "Speak like a podcast host roasting the listener's financial habits. "
    "Energetic, funny, slightly sarcastic."
)


def generate_speech(client: OpenAI, text: str, topic: str, voice: str = "coral") -> str:
    """Convert *text* to speech using OpenAI TTS and save as MP3. Returns file path."""
    PODCASTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    slug = topic.lower().replace(" ", "-")[:30]
    filepath = PODCASTS_DIR / f"{timestamp}_{slug}.mp3"

    try:
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text,
            instructions=TTS_VOICE_INSTRUCTIONS,
        ) as response:
            response.stream_to_file(str(filepath))
    except openai.APIConnectionError as e:
        raise RuntimeError(f"Could not connect to OpenAI API for TTS: {e}") from e
    except openai.APIError as e:
        raise RuntimeError(f"OpenAI TTS API error: {e}") from e
    except OSError as e:
        raise RuntimeError(f"Failed to write audio file: {e}") from e

    # Rough cost estimate for TTS (input text tokens + audio output tokens)
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

    return str(filepath)
