import os
import uuid
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
import edge_tts

# Handle absolute import issues since groq_service is in services
from services.groq_service import translate_text
import time

router = APIRouter()

# Same supported languages as translate.py
SUPPORTED_LANGUAGES = {
    "vi": "Vietnamese",
    "en": "English",
    "zh": "Chinese",
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

# Mapping language codes to Edge TTS voices
VOICE_MAP = {
    "vi": "vi-VN-HoaiMyNeural",
    "en": "en-US-AriaNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "es": "es-ES-ElviraNeural",
    "th": "th-TH-PremwadeeNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "ar": "ar-EG-SalmaNeural",
    "pt": "pt-PT-RaquelNeural",
    "it": "it-IT-ElsaNeural",
    "hi": "hi-IN-SwaraNeural"
}

# Ensure static folder exists
OUTPUT_DIR = "static/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cleanup old files occasionally (if older than 1 hour)
def cleanup_old_files():
    now = time.time()
    try:
        for filename in os.listdir(OUTPUT_DIR):
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(file_path):
                if now - os.path.getctime(file_path) > 3600:
                    os.remove(file_path)
    except Exception:
        pass


@router.post("/tts")
async def process_tts(
    text: str = Form(...),
    source_language: str = Form(...),
    target_language: str = Form(...),
):
    """
    Generate voice from text. Validates and translates if needed.
    """
    # 1. Validation
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if source_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported source language: {source_language}")
    
    if target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported target language: {target_language}")

    cleanup_old_files()

    try:
        # 2. Translation (Skip if source == target)
        final_text = text.strip()
        if source_language != target_language:
            final_text = await translate_text(
                text=final_text,
                source_language=SUPPORTED_LANGUAGES[source_language],
                target_language=SUPPORTED_LANGUAGES[target_language]
            )

        # 3. Generate Audio with edge-tts
        voice = VOICE_MAP.get(target_language, "en-US-AriaNeural")
        communicate = edge_tts.Communicate(final_text, voice)
        
        file_name = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        
        await communicate.save(file_path)
        
        audio_url = f"/static/audio/{file_name}"
        
        return JSONResponse(
            content={
                "success": True,
                "original_text": text,
                "translated_text": final_text,
                "source_language": SUPPORTED_LANGUAGES[source_language],
                "target_language": SUPPORTED_LANGUAGES[target_language],
                "audio_url": audio_url
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")
