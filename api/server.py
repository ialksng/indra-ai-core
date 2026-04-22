import asyncio
import os
import uuid
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from faster_whisper import WhisperModel
from elevenlabs import generate, stream
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🔊 MODELS
# =========================
whisper = WhisperModel("base", compute_type="int8")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# =========================
# 🧠 AI TEXT
# =========================
def generate_ai(prompt):
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "You are Indra AI."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=20
        )

        return res.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "AI unavailable"

# =========================
# 🎤 TRANSCRIBE
# =========================
def transcribe(audio_bytes):
    try:
        segments, _ = whisper.transcribe(audio_bytes)
        return " ".join([s.text for s in segments])
    except:
        return ""

# =========================
# 🔊 TTS STREAM
# =========================
def tts_stream(text):
    audio_stream = generate(
        text=text,
        voice="Rachel",
        model="eleven_monolingual_v1",
        stream=True
    )
    for chunk in audio_stream:
        yield chunk

# =========================
# 🌐 ROOT
# =========================
@app.get("/")
def root():
    return {"status": "Indra streaming AI running"}

# =========================
# 🎤 WEBSOCKET STREAM
# =========================
@app.websocket("/ws/voice")
async def voice_ws(ws: WebSocket):
    await ws.accept()

    buffer = b""
    speaking = False

    try:
        while True:
            data = await ws.receive()

            # 🔥 INTERRUPT
            if "text" in data and data["text"] == "interrupt":
                speaking = False
                continue

            if "bytes" in data:
                buffer += data["bytes"]

            # process chunk
            if len(buffer) > 32000:
                text = transcribe(buffer)
                buffer = b""

                if not text:
                    continue

                # 🔥 WAKE WORD
                if "indra" not in text.lower():
                    continue

                await ws.send_json({
                    "type": "transcript",
                    "text": text
                })

                response = generate_ai(text)

                await ws.send_json({
                    "type": "response",
                    "text": response
                })

                # 🔊 STREAM AUDIO
                speaking = True
                for chunk in tts_stream(response):
                    if not speaking:
                        break

                    await ws.send_bytes(chunk)

    except Exception as e:
        print("WS closed:", e)

# =========================
# 🎤 FALLBACK (OLD /voice)
# =========================
@app.post("/voice")
async def voice(file: UploadFile = File(...)):
    content = await file.read()

    text = transcribe(content)
    response = generate_ai(text)

    filename = f"{uuid.uuid4()}.mp3"
    filepath = f"/tmp/{filename}"

    audio = generate(
        text=response,
        voice="Rachel",
        model="eleven_monolingual_v1"
    )

    with open(filepath, "wb") as f:
        f.write(audio)

    return {
        "input_text": text,
        "response": response,
        "audio_url": f"/audio/{filename}"
    }

@app.get("/audio/{filename}")
def get_audio(filename: str):
    return FileResponse(f"/tmp/{filename}")