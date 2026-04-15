import os
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

_client: AsyncGroq | None = None


def get_groq_client() -> AsyncGroq:
    """Singleton Groq async client."""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in environment variables.")
        _client = AsyncGroq(api_key=api_key)
    return _client


async def transcribe_audio(file_path: str, language: str) -> str:
    """
    Transcribe audio file using Groq Whisper API.

    Args:
        file_path: Local path to the audio file.
        language: ISO 639-1 language code (e.g. 'vi', 'en').

    Returns:
        Transcribed text string.
    """
    client = get_groq_client()

    with open(file_path, "rb") as audio_file:
        response = await client.audio.transcriptions.create(
            file=(os.path.basename(file_path), audio_file),
            model="whisper-large-v3",
            language=language,
            response_format="text",
        )

    # response is a plain string when response_format="text"
    return str(response).strip()


async def translate_text(text: str, source_language: str, target_language: str) -> str:
    """
    Translate text using Groq LLM (llama-3.3-70b-versatile).

    Args:
        text: Source text to translate.
        source_language: Full language name (e.g. 'Vietnamese').
        target_language: Full target language name (e.g. 'English').

    Returns:
        Translated text string.
    """
    client = get_groq_client()

    system_prompt = (
        "You are a professional translator. "
        "Your task is to translate the given text accurately and naturally. "
        "Return ONLY the translated text — no explanations, no notes, no quotation marks."
        "If the text is Chinese, translate it to Simplified Chinese."
    )

    user_prompt = (
        f"Translate the following text from {source_language} to {target_language}:\n\n"
        f"{text}"
    )

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=2048,
    )

    translated = response.choices[0].message.content or ""
    return translated.strip()
