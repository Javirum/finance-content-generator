import os
import re
from pathlib import Path

from PyPDF2 import PdfReader
from docx import Document


# Extensions mapped to format labels
TEXT_EXTENSIONS = {".md", ".txt"}
PDF_EXTENSIONS = {".pdf"}
DOCX_EXTENSIONS = {".docx"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg"}

YOUTUBE_PATTERN = re.compile(
    r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+"
)


def detect_format(source: str) -> str:
    """Return a format label for a file path or URL."""
    if YOUTUBE_PATTERN.match(source):
        return "YOUTUBE"
    ext = Path(source).suffix.lower()
    if ext in TEXT_EXTENSIONS:
        return "MD" if ext == ".md" else "TXT"
    if ext in PDF_EXTENSIONS:
        return "PDF"
    if ext in DOCX_EXTENSIONS:
        return "DOCX"
    if ext in AUDIO_EXTENSIONS:
        return "AUDIO"
    return "UNKNOWN"


def extract_text(source: str, openai_client=None) -> str:
    """Extract text content from a supported file or URL.

    Args:
        source: File path or YouTube URL.
        openai_client: An OpenAI client instance, required for audio transcription.

    Returns:
        The extracted text content.

    Raises:
        ValueError: If the format is unsupported or extraction fails.
    """
    fmt = detect_format(source)

    if fmt in ("MD", "TXT"):
        return _read_text_file(source)
    if fmt == "PDF":
        return _read_pdf(source)
    if fmt == "DOCX":
        return _read_docx(source)
    if fmt == "AUDIO":
        return _transcribe_audio(source, openai_client)
    if fmt == "YOUTUBE":
        return _fetch_youtube_transcript(source)

    raise ValueError(f"Unsupported file format: {source}")


def _read_text_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        raise ValueError(f"Could not read text file {path}: {e}") from e
    except UnicodeDecodeError as e:
        raise ValueError(f"Encoding error reading {path}: {e}") from e


def _read_pdf(path: str) -> str:
    try:
        reader = PdfReader(path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages).strip()
    except Exception as e:
        raise ValueError(f"Could not read PDF {path}: {e}") from e


def _read_docx(path: str) -> str:
    try:
        doc = Document(path)
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        raise ValueError(f"Could not read DOCX {path}: {e}") from e


def _transcribe_audio(path: str, openai_client) -> str:
    if openai_client is None:
        raise ValueError("OpenAI client is required for audio transcription.")
    try:
        with open(path, "rb") as audio_file:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        return transcription.text
    except Exception as e:
        raise ValueError(f"Audio transcription failed for {path}: {e}") from e


def _fetch_youtube_transcript(url: str) -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        video_id_match = re.search(r"(?:v=|youtu\.be/)([\w-]+)", url)
        if not video_id_match:
            raise ValueError(f"Could not extract video ID from URL: {url}")
        video_id = video_id_match.group(1)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(entry["text"] for entry in transcript)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to fetch YouTube transcript for {url}: {e}") from e
