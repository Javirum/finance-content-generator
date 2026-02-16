import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gpt-5-nano"


def get_client() -> OpenAI:
    """Create and return an OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-key-here":
        raise RuntimeError(
            "OPENAI_API_KEY not set. Add your key to the .env file."
        )
    return OpenAI(api_key=api_key)


def generate(client: OpenAI, messages: list[dict], model: str = DEFAULT_MODEL, temperature: float = 0.9) -> str:
    """Send messages to OpenAI and return the response text."""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
