import os
import uuid
import requests

from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from faster_whisper import WhisperModel
from elevenlabs.client import ElevenLabs

# =========================
# 🔑 ENV SETUP
# =========================
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# =========================
# 🚀 APP
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🎤 MODELS (RENDER SAFE)
# =========================
whisper = WhisperModel("tiny", compute_type="int8")

eleven_client = ElevenLabs(api_key=ELEVEN_API_KEY) if ELEVEN_API_KEY else None

# =========================
# 🧠 AI TEXT (GROQ)
# =========================
def generate_ai(prompt):
    if not GROQ_API_KEY:
        return "AI unavailable"

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

        if res.status_code != 200:
            print("❌ GROQ ERROR:", res.text)
            return "AI unavailable"

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
    except Exception as e:
        print("WHISPER ERROR:", e)
        return ""

# =========================
# 🔊 TTS (ELEVENLABS)
# =========================
def generate_tts(text):
    if not ELEVEN_API_KEY or not eleven_client:
        print("❌ ELEVENLABS_API_KEY missing")
        return None

    if not text or text.strip() == "":
        return None

    try:
        audio_stream = eleven_client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            model_id="eleven_monolingual_v1",
            text=text
        )

        audio_bytes = b"".join(chunk for chunk in audio_stream if chunk)
        return audio_bytes

    except Exception as e:
        print("❌ TTS ERROR:", str(e))
        return None

# =========================
# 🌐 ROOT
# =========================
@app.get("/")
def root():
    return {"status": "Indra AI running"}

@app.get("/ping")
def ping():
    return {"status": "alive"}

# =========================
# 🎤 WEBSOCKET VOICE
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

                # 🔊 AUDIO
                speaking = True
                audio = generate_tts(response)

                if audio and speaking:
                    await ws.send_bytes(audio)

    except Exception as e:
        print("WS closed:", e)

# =========================
# 🎤 FALLBACK VOICE
# =========================
@app.post("/voice")
async def voice(file: UploadFile = File(...)):
    content = await file.read()

    text = transcribe(content)
    response = generate_ai(text)

    filename = f"{uuid.uuid4()}.mp3"
    filepath = f"/tmp/{filename}"

    audio = generate_tts(response)

    if audio:
        with open(filepath, "wb") as f:
            f.write(audio)

    return {
        "input_text": text,
        "response": response,
        "audio_url": f"/audio/{filename}"
    }

# =========================
# 🔊 AUDIO SERVE
# =========================
@app.get("/audio/{filename}")
def get_audio(filename: str):
    return FileResponse(f"/tmp/{filename}")