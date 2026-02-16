#!/usr/bin/env python3
"""MoneySavvy AI — Gen Z Financial Coach Content Engine"""

import os
import shlex

from src.llm_client import get_client
from src.knowledge_base import KnowledgeBase
from src.prompts import PromptManager
from src.generator import generate_tweet, generate_thread, save_output

KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")

HELP_TEXT = """
Available commands:
  list                                  Show loaded knowledge base files
  add <filepath|URL>                    Add a file or YouTube URL to the KB
  remove <#>                            Remove a file from the KB by number
  prompt                                Show the current system prompt
  prompt edit                           Edit the system prompt in your default editor
  prompt reset                          Restore the default system prompt
  generate --topic <topic> [options]    Generate content
    --topic   "topic"                   Required: the topic or scenario
    --style   educational|motivational|myth-busting   (default: educational)
    --type    tweet|thread              (default: tweet)
  help                                  Show this help message
  quit / exit                           Exit the session
"""


def parse_generate_args(parts: list[str]) -> dict:
    """Parse arguments for the generate command."""
    args = {"topic": None, "style": "educational", "type": "tweet"}
    i = 0
    while i < len(parts):
        if parts[i] == "--topic" and i + 1 < len(parts):
            args["topic"] = parts[i + 1]
            i += 2
        elif parts[i] == "--style" and i + 1 < len(parts):
            args["style"] = parts[i + 1]
            i += 2
        elif parts[i] == "--type" and i + 1 < len(parts):
            args["type"] = parts[i + 1]
            i += 2
        else:
            i += 1
    return args


def main():
    print("\n=== MoneySavvy AI — Content Engine ===\n")

    # Initialize OpenAI client
    try:
        client = get_client()
    except RuntimeError as e:
        print(f"Error: {e}")
        return

    # Load knowledge base
    kb = KnowledgeBase(KB_DIR, openai_client=client)
    print("Loading knowledge base...")
    kb.load_all()
    kb.display()

    # Load prompt manager
    prompt_mgr = PromptManager()
    print("System prompt loaded from disk.")
    print('Type "help" for available commands.\n')

    # Interactive loop
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not raw:
            continue

        try:
            parts = shlex.split(raw)
        except ValueError:
            parts = raw.split()

        cmd = parts[0].lower()

        if cmd in ("quit", "exit"):
            print("Goodbye!")
            break

        elif cmd == "help":
            print(HELP_TEXT)

        elif cmd == "list":
            kb.display()

        elif cmd == "add":
            if len(parts) < 2:
                print("Usage: add <filepath|URL>")
                continue
            source = parts[1]
            try:
                entry = kb.add(source)
                print(f"Added: {entry.name} ({entry.fmt}) ({len(kb.list_entries())} files loaded)")
            except Exception as e:
                print(f"Error adding file: {e}")

        elif cmd == "remove":
            if len(parts) < 2:
                print("Usage: remove <number>")
                continue
            try:
                index = int(parts[1])
                entry = kb.remove(index)
                print(f"Removed: {entry.name} ({len(kb.list_entries())} files loaded)")
            except (ValueError, IndexError) as e:
                print(f"Error: {e}")

        elif cmd == "prompt":
            if len(parts) == 1:
                prompt_mgr.display()
            elif parts[1].lower() == "edit":
                prompt_mgr.edit()
            elif parts[1].lower() == "reset":
                prompt_mgr.reset()
            else:
                print("Usage: prompt | prompt edit | prompt reset")

        elif cmd == "generate":
            args = parse_generate_args(parts[1:])
            if not args["topic"]:
                print('Usage: generate --topic "your topic" [--style educational] [--type tweet]')
                continue

            content_type = args["type"]
            topic = args["topic"]
            style = args["style"]

            print(f"\nGenerating {content_type} on \"{topic}\" ({style})...\n")

            try:
                if content_type == "thread":
                    content = generate_thread(client, kb, prompt_mgr, topic, style)
                else:
                    content = generate_tweet(client, kb, prompt_mgr, topic, style)

                print(content)
                print()

                filepath = save_output(content, topic)
                print(f"Saved to: {filepath}\n")
            except Exception as e:
                print(f"Error generating content: {e}\n")

        else:
            print(f'Unknown command: "{cmd}". Type "help" for available commands.')


if __name__ == "__main__":
    main()
