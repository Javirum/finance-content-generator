import os
import shutil
import subprocess
import sys
from pathlib import Path


PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
SYSTEM_PROMPT_PATH = os.path.join(PROMPTS_DIR, "system_prompt.md")
DEFAULT_PROMPT_PATH = os.path.join(PROMPTS_DIR, "system_prompt.default.md")
TEMPLATES_DIR = os.path.join(PROMPTS_DIR, "templates")


class PromptManager:
    """Manages the system prompt (load from disk, edit, reset) and tweet templates."""

    def __init__(self):
        self._system_prompt: str = ""
        self._ensure_system_prompt_exists()
        self._load()

    def _ensure_system_prompt_exists(self) -> None:
        """On first run, copy default → active if active doesn't exist."""
        if not os.path.exists(SYSTEM_PROMPT_PATH):
            shutil.copy2(DEFAULT_PROMPT_PATH, SYSTEM_PROMPT_PATH)

    def _load(self) -> None:
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            self._system_prompt = f.read().strip()

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    def display(self) -> None:
        """Print the current system prompt."""
        print(f"\nCurrent system prompt (from {SYSTEM_PROMPT_PATH}):")
        print("-" * 50)
        print(self._system_prompt)
        print("-" * 50)
        print()

    def edit(self) -> None:
        """Open the system prompt in the user's default editor."""
        editor = os.environ.get("EDITOR", "nano" if sys.platform != "win32" else "notepad")
        print(f"Opening system prompt in {editor}...")
        subprocess.run([editor, SYSTEM_PROMPT_PATH])
        self._load()
        print("System prompt updated and reloaded.")

    def reset(self) -> None:
        """Restore system prompt to default."""
        shutil.copy2(DEFAULT_PROMPT_PATH, SYSTEM_PROMPT_PATH)
        self._load()
        print("System prompt restored to default.")

    def load_template(self, template_name: str) -> str:
        """Load a tweet template by name (e.g. 'tweet_single')."""
        path = os.path.join(TEMPLATES_DIR, f"{template_name}.md")
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def build_messages(self, kb_context: str, topic: str, style: str = "educational", template: str = "tweet_single") -> list[dict]:
        """Assemble the full message list for the OpenAI API.

        Returns a list of messages: [system, user].
        """
        try:
            tweet_template = self.load_template(template)
        except FileNotFoundError:
            tweet_template = ""

        user_content = ""
        if kb_context:
            user_content += f"## Knowledge Base Context\n\n{kb_context}\n\n---\n\n"
        if tweet_template:
            user_content += f"## Instructions\n\n{tweet_template}\n\n---\n\n"
        user_content += f"## Request\n\nTopic: {topic}\nStyle: {style}\n"

        return [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": user_content},
        ]
