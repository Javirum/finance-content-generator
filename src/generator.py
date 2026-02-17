import os
from datetime import datetime

from src.knowledge_base import KnowledgeBase
from src.prompts import PromptManager
from src.llm_client import generate as llm_generate

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "generated")
BRAND_GUIDELINES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "knowledge_base", "primary", "brand-guidelines.md",
)


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
    with open(BRAND_GUIDELINES_PATH, "r", encoding="utf-8") as f:
        brand_guidelines = f.read().strip()

    kb_context = kb.get_context()
    messages = prompt_mgr.build_messages(
        kb_context=kb_context,
        topic=topic,
        weekday=weekday,
        instructions=brand_guidelines,
    )
    return llm_generate(client, messages)


def save_output(content: str, topic: str) -> str:
    """Save generated content to output/generated/ with a timestamp. Returns the file path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    slug = topic.lower().replace(" ", "-")[:30]
    filename = f"{timestamp}_{slug}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Topic: {topic}\n\n{content}\n")
    return filepath
