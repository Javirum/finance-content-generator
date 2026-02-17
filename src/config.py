"""Centralized paths and constants for MoneySavvy AI."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
KB_DIR = PROJECT_ROOT / "knowledge_base"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
SYSTEM_PROMPT_PATH = PROMPTS_DIR / "system_prompt.md"
DEFAULT_PROMPT_PATH = PROMPTS_DIR / "system_prompt.default.md"
TEMPLATES_DIR = PROMPTS_DIR / "templates"
OUTPUT_DIR = PROJECT_ROOT / "output" / "generated"
PODCASTS_DIR = PROJECT_ROOT / "output" / "podcasts"
USAGE_DIR = PROJECT_ROOT / "output" / "usage"
USAGE_FILE = USAGE_DIR / "usage_log.json"
BRAND_GUIDELINES_PATH = KB_DIR / "primary" / "brand-guidelines.md"

DEFAULT_MODEL = "gpt-5.2"
PRICING = {
    "gpt-5.2": {"input": 1.75, "cached_input": 0.175, "output": 14.00},
    "gpt-4o-mini-tts": {"input": 0.60, "output": 12.00},
}
