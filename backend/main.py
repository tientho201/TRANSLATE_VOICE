from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import translate, tts

app = FastAPI(
    title="Voice Translate API",
    description="Transcribe and translate audio files using Groq API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(translate.router, prefix="/api/v1", tags=["Translate"])
app.include_router(tts.router, prefix="/api/v1", tags=["TTS"])

import os
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Voice Translate API"}
