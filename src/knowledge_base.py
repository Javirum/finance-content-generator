from __future__ import annotations

import logging
import os
from pathlib import Path

from src.file_processor import detect_format, extract_text

logger = logging.getLogger(__name__)


class KBEntry:
    """A single loaded knowledge base document."""

    def __init__(self, source: str, fmt: str, content: str):
        self.source = source
        self.fmt = fmt
        self.content = content

    @property
    def name(self) -> str:
        return os.path.basename(self.source)

    @property
    def size_kb(self) -> float:
        return len(self.content.encode("utf-8")) / 1024


class KnowledgeBase:
    """Loads knowledge base files once, holds them in memory, supports add/remove."""

    def __init__(self, kb_dir: str, openai_client=None):
        self._entries: list[KBEntry] = []
        self._kb_dir = str(kb_dir)
        self._openai_client = openai_client

    def load_all(self) -> None:
        """Load all files from primary/ and secondary/ subdirectories."""
        for subdir in ("primary", "secondary"):
            dir_path = os.path.join(self._kb_dir, subdir)
            if not os.path.isdir(dir_path):
                continue
            for filename in sorted(os.listdir(dir_path)):
                filepath = os.path.join(dir_path, filename)
                if os.path.isfile(filepath):
                    entry = self._load_file(filepath)
                    if entry is not None:
                        self._entries.append(entry)

    def _load_file(self, source: str) -> KBEntry | None:
        try:
            fmt = detect_format(source)
            if fmt == "AUDIO":
                print(f"  Transcribing {os.path.basename(source)} via Whisper API...")
            if fmt == "YOUTUBE":
                print(f"  Fetching YouTube transcript...")
            content = extract_text(source, self._openai_client)
            return KBEntry(source=source, fmt=fmt, content=content)
        except Exception as e:
            logger.warning("Failed to load %s: %s", source, e)
            return None

    def add(self, source: str) -> KBEntry:
        """Add a new file or URL to the knowledge base."""
        fmt = detect_format(source)
        if fmt == "UNKNOWN":
            raise ValueError(f"Unsupported format: {source}")
        entry = self._load_file(source)
        if entry is None:
            raise ValueError(f"Failed to load: {source}")
        self._entries.append(entry)
        return entry

    def remove(self, index: int) -> KBEntry:
        """Remove a file by its 1-based index."""
        if index < 1 or index > len(self._entries):
            raise IndexError(
                f"Invalid index {index}. Must be between 1 and {len(self._entries)}."
            )
        return self._entries.pop(index - 1)

    def list_entries(self) -> list[KBEntry]:
        return list(self._entries)

    def get_context(self) -> str:
        """Return all loaded documents as a single context string."""
        parts = []
        for entry in self._entries:
            parts.append(f"### {entry.name}\n{entry.content}")
        return "\n\n---\n\n".join(parts)

    def display(self) -> None:
        """Print the loaded files list to the terminal."""
        count = len(self._entries)
        if count == 0:
            print("Knowledge Base is empty. Use 'add <path>' to load files.")
            return
        print(f"\nKnowledge Base ({count} file{'s' if count != 1 else ''}):")
        for i, entry in enumerate(self._entries, 1):
            relative = entry.source
            if self._kb_dir and entry.source.startswith(self._kb_dir):
                relative = os.path.relpath(entry.source, self._kb_dir)
            print(f"  [{i}] {relative:<45} ({entry.fmt:<6}) {entry.size_kb:.1f} KB")
        print()
