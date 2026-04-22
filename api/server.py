import os
import uuid
import requests
import io
import wave

from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from elevenlabs.client import ElevenLabs

# =========================
# 🔑 ENV
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")

eleven_client = ElevenLabs(api_key=ELEVEN_API_KEY) if ELEVEN_API_KEY else None

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
# 🛠️ HELPER: WRAP PCM TO WAV
# =========================
def create_wav_buffer(pcm_data):
    """Converts Raw 16-bit PCM bytes into a valid WAV file in memory"""
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(1)      # Mono
        wav_file.setsampwidth(2)      # 16-bit
        wav_file.setframerate(16000)  # 16kHz
        wav_file.writeframes(pcm_data)
    wav_io.seek(0)
    return wav_io

# =========================
# 🎤 TRANSCRIBE (GROQ)
# =========================
def transcribe(audio_bytes):
    if not GROQ_API_KEY:
        return ""

    # Convert the raw bytes from React into a valid WAV format for Groq
    wav_file = create_wav_buffer(audio_bytes)

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            files={"file": ("audio.wav", wav_file, "audio/wav")}, # ✅ FIXED FORMAT
            data={"model": "whisper-large-v3", "language": "en"},
            timeout=15
        )

        if res.status_code != 200:
            print("❌ STT ERROR:", res.text)
            return ""

        text = res.json().get("text", "").strip()
        print(f"🎙️ Heard: {text}")
        return text

    except Exception as e:
        print("❌ STT EXCEPTION:", e)
        return ""

# =========================
# 🧠 AI TEXT (GROQ FIXED)
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
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are Indra AI. Keep responses brief and conversational."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=15
        )

        if res.status_code != 200:
            print("❌ GROQ ERROR:", res.text)
            return "AI unavailable"

        data = res.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "AI unavailable")

    except Exception as e:
        print("❌ AI ERROR:", e)
        return "AI unavailable"

# =========================
# 🔊 TTS (SAFE)
# =========================
def generate_tts(text):
    if not ELEVEN_API_KEY or not eleven_client:
        return None

    try:
        audio_stream = eleven_client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            model_id="eleven_monolingual_v1",
            text=text
        )

        return b"".join(chunk for chunk in audio_stream if chunk)

    except Exception as e:
        print("❌ TTS ERROR:", e)
        return None

# =========================
# 🌐 ROOT & API
# =========================
@app.get("/")
def root():
    return {"status": "Indra AI running"}

@app.post("/chat")
async def chat(req: dict):
    try:
        message = req.get("message", "")
        if not message:
            return {"message": "Message required", "actions": []}
        response = generate_ai(message)
        return {"message": str(response), "actions": []}
    except Exception as e:
        return {"message": "AI error", "actions": []}

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

            if "text" in data and data["text"] == "interrupt":
                speaking = False
                continue

            if "bytes" in data:
                buffer += data["bytes"]

            # ✅ INCREASED BUFFER TO ~3 SECONDS SO IT CAN HEAR "INDRA"
            if len(buffer) > 96000: 
                audio_to_process = buffer
                buffer = b"" # Reset buffer immediately so we don't miss next audio

                text = transcribe(audio_to_process)

                if not text:
                    continue

                await ws.send_json({"type": "transcript", "text": text})

                # Check wake word (make it a bit forgiving regarding punctuation)
                if "indra" not in text.lower():
                    continue

                response = generate_ai(text)

                await ws.send_json({"type": "response", "text": response})

                speaking = True

                audio = generate_tts(response[:500])

                if audio and speaking:
                    await ws.send_bytes(audio)

    except Exception as e:
        print("WS closed:", e)

# =========================
# 🎤 FALLBACK
# =========================
@app.post("/voice")
async def voice(file: UploadFile = File(...)):
    content = await file.read()
    text = transcribe(content)
    response = generate_ai(text)
    
    filename = f"{uuid.uuid4()}.mp3"
    filepath = f"/tmp/{filename}"
    audio = generate_tts(response[:500])

    if audio:
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