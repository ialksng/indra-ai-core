from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from core.brain import chat
from modules.audio.stt import speech_to_text
from modules.audio.tts import text_to_speech

import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------ MODELS ------------------

class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: str = "lite"
    agent: bool = False


# ------------------ BASIC ROUTES ------------------

@app.get("/")
def root():
    return {"status": "Indra AI running"}


@app.get("/ping")
def ping():
    return {"status": "alive"}


# ------------------ TEXT CHAT ------------------

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    return chat(req.user_id, req.message, req.mode, req.agent)


# ------------------ VOICE CHAT ------------------

@app.post("/voice")
async def voice_chat(
    file: UploadFile = File(...),
    user_id: str = "voice_user",
    mode: str = "smart"
):
    try:
        audio_bytes = await file.read()

        # 🎤 Speech → Text
        text = speech_to_text(audio_bytes)

        if not text:
            return {"error": "Speech recognition failed"}

        # 🧠 AI Response
        ai_response = chat(user_id, text, mode)

        # 🔊 Text → Speech
        audio_file = text_to_speech(ai_response["message"])

        return {
            "input_text": text,
            "response": ai_response["message"],
            "audio_url": f"/audio/{os.path.basename(audio_file)}"
        }

    except Exception as e:
        print("❌ VOICE ERROR:", e)
        return {"error": "Voice processing failed"}


# ------------------ SERVE AUDIO ------------------

@app.get("/audio/{filename}")
def get_audio(filename: str):
    file_path = f"/tmp/{filename}"

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(file_path, media_type="audio/mpeg")