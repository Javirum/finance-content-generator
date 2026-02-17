import os
from datetime import datetime

from src.config import OUTPUT_DIR, BRAND_GUIDELINES_PATH
from src.knowledge_base import KnowledgeBase
from src.prompts import PromptManager
from src.llm_client import generate as llm_generate


def generate_tweet(client, kb: KnowledgeBase, prompt_mgr: PromptManager, topic: str, style: str = "educational") -> str:
    """Generate a single tweet using the loaded KB and system prompt."""
    kb_context = kb.get_context()
    messages = prompt_mgr.build_messages(
        kb_context=kb_context,
        topic=topic,
        style=style,
        template="tweet_single",
    )
    tweet = llm_generate(client, messages)

    # Validate length — retry once if too long
    if len(tweet) > 280:
        messages.append({"role": "assistant", "content": tweet})
        messages.append({
            "role": "user",
            "content": "This tweet is over 280 characters. Rewrite it to be under 280 characters while keeping the same message.",
        })
        tweet = llm_generate(client, messages)

    return tweet


def generate_thread(client, kb: KnowledgeBase, prompt_mgr: PromptManager, topic: str, style: str = "educational", count: int = 3) -> str:
    """Generate a tweet thread using the loaded KB and system prompt."""
    kb_context = kb.get_context()
    messages = prompt_mgr.build_messages(
        kb_context=kb_context,
        topic=topic,
        style=style,
        template="tweet_thread",
    )
    # Override the default tweet count from the template
    messages.append({
        "role": "user",
        "content": f"Generate exactly {count} tweets in this thread.",
    })
    return llm_generate(client, messages)


def generate_daily_content(client, kb: KnowledgeBase, prompt_mgr: PromptManager, topic: str, weekday: str) -> str:
    """Generate all 3 tweets for a given weekday using the brand guidelines."""
    try:
        with open(BRAND_GUIDELINES_PATH, "r", encoding="utf-8") as f:
            brand_guidelines = f.read().strip()
    except FileNotFoundError:
        raise RuntimeError(
            f"Brand guidelines file not found at: {BRAND_GUIDELINES_PATH}"
        ) from None

    kb_context = kb.get_context()
    messages = prompt_mgr.build_messages(
        kb_context=kb_context,
        topic=topic,
        weekday=weekday,
        instructions=brand_guidelines,
    )
    return llm_generate(client, messages)


def generate_podcast_script(client, kb: KnowledgeBase, prompt_mgr: PromptManager, topic: str, tweets: str) -> str:
    """Generate a ~1 minute podcast script using the tweets as context."""
    kb_context = kb.get_context()

    user_content = ""
    if kb_context:
        user_content += f"## Knowledge Base Context\n\n{kb_context}\n\n---\n\n"

    user_content += (
        "## Request\n\n"
        "Write a 1-minute financial roast podcast script (~150 words) using the tweets below as guidelines.\n"
        "Tone: humorous, roast-style, Gen Z voice, but educational underneath.\n"
        "Do NOT include stage directions, sound effects, or speaker labels — just the spoken monologue.\n\n"
        f"### Topic: {topic}\n\n"
        f"### Tweets\n\n{tweets}\n"
    )

    messages = [
        {"role": "system", "content": prompt_mgr.system_prompt},
        {"role": "user", "content": user_content},
    ]
    return llm_generate(client, messages)


def save_output(content: str, topic: str) -> str:
    """Save generated content to output/generated/ with a timestamp. Returns the file path."""
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        slug = topic.lower().replace(" ", "-")[:30]
        filename = f"{timestamp}_{slug}.md"
        filepath = OUTPUT_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Topic: {topic}\n\n{content}\n")
    except OSError as e:
        raise RuntimeError(f"Failed to save output file: {e}") from e
    return str(filepath)
