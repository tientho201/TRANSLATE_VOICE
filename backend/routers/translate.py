import tempfile
import os
import subprocess
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from services.groq_service import transcribe_audio, translate_text

# Lấy đường dẫn ffmpeg từ imageio-ffmpeg (Python package, không cần cài system ffmpeg)
def _get_ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"  # fallback nếu imageio-ffmpeg chưa cài

router = APIRouter()

SUPPORTED_LANGUAGES = {
    "vi": "Vietnamese",
    "en": "English",
    "zh": "Simplified Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "th": "Thai",
    "ru": "Russian",
    "ar": "Arabic",
    "pt": "Portuguese",
    "it": "Italian",
    "hi": "Hindi",
}

# Groq Whisper natively supported formats
GROQ_SUPPORTED = {".flac", ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".ogg", ".opus", ".wav", ".webm"}

# Extra formats we accept and auto-convert to .wav
CONVERTIBLE = {".aac", ".wma", ".amr", ".3gp", ".3gpp"}

AUDIO_EXTENSIONS = GROQ_SUPPORTED | CONVERTIBLE


def _convert_to_wav(src_path: str) -> str:
    """Convert audio file to .wav using ffmpeg directly (via imageio-ffmpeg). No pydub needed."""
    ffmpeg_exe = _get_ffmpeg_exe()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as out_tmp:
        out_path = out_tmp.name

    try:
        result = subprocess.run(
            [
                ffmpeg_exe, "-y",       # -y: overwrite output nếu tồn tại
                "-i", src_path,         # input file
                "-ar", "16000",         # sample rate 16kHz (tối ưu cho Whisper)
                "-ac", "1",             # mono channel
                "-f", "wav",            # output format
                out_path,
            ],
            capture_output=True,
            timeout=60,
        )
        if result.returncode != 0:
            err = result.stderr.decode(errors="ignore")[-500:]  # lấy 500 ký tự cuối
            raise RuntimeError(f"ffmpeg exited with code {result.returncode}: {err}")
    except FileNotFoundError:
        raise RuntimeError(
            f"ffmpeg not found at '{ffmpeg_exe}'. Make sure imageio-ffmpeg is installed: pip install imageio-ffmpeg"
        )

    return out_path


@router.post("/translate")
async def translate_voice(
    audio_file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...),
):
    """
    Transcribe audio file and translate to target language.

    - **audio_file**: Audio file to transcribe (mp3, wav, m4a, aac, webm, ogg, flac, etc.)
    - **source_language**: Source language code (e.g. 'vi', 'en', 'zh')
    - **target_language**: Target language code to translate into
    """
    # Validate language codes
    if source_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported source language: {source_language}")
    if target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported target language: {target_language}")
    if source_language == target_language:
        raise HTTPException(status_code=400, detail="Source and target languages must be different")

    # Validate file extension
    original_filename = audio_file.filename or "audio"
    ext = os.path.splitext(original_filename)[1].lower()
    if ext not in AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format '{ext}'. Supported: {', '.join(sorted(AUDIO_EXTENSIONS))}",
        )

    # Save uploaded file to temp
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await audio_file.read()
            tmp.write(content)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save audio file: {str(e)}")

    converted_path: str | None = None

    try:
        # Auto-convert formats not supported by Groq (e.g. .aac) → .wav
        if ext in CONVERTIBLE:
            try:
                converted_path = _convert_to_wav(tmp_path)
                process_path = converted_path
            except Exception as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Cannot convert '{ext}' to wav. Make sure ffmpeg is installed. Detail: {str(e)}",
                )
        else:
            process_path = tmp_path

        # Step 1: Transcribe audio
        transcribed_text = await transcribe_audio(process_path, source_language)

        if not transcribed_text or not transcribed_text.strip():
            raise HTTPException(status_code=422, detail="Could not transcribe audio. Please speak clearly and try again.")

        # Step 2: Translate text
        translated_text = await translate_text(
            text=transcribed_text,
            source_language=SUPPORTED_LANGUAGES[source_language],
            target_language=SUPPORTED_LANGUAGES[target_language],
        )

        return JSONResponse(
            content={
                "success": True,
                "source_language": SUPPORTED_LANGUAGES[source_language],
                "target_language": SUPPORTED_LANGUAGES[target_language],
                "transcribed_text": transcribed_text,
                "translated_text": translated_text,
                "converted": ext in CONVERTIBLE,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # Clean up temp files — on Windows the file may still be locked
        # by pydub/ffmpeg briefly, so we suppress PermissionError gracefully.
        import gc
        gc.collect()  # encourage Python to release any open file handles
        for path in [tmp_path, converted_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except PermissionError:
                    pass  # Windows lock — OS will clean it up on its own


@router.get("/languages")
async def get_supported_languages():
    """Return list of supported languages."""
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ]
    }
