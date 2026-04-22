import os
from elevenlabs.client import ElevenLabs

ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# initialize once
eleven_client = ElevenLabs(api_key=ELEVEN_API_KEY) if ELEVEN_API_KEY else None


def generate_tts(text):
    if not ELEVEN_API_KEY or not eleven_client:
        print("❌ ELEVENLABS_API_KEY missing or client not initialized")
        return None

    if not text or text.strip() == "":
        return None

    try:
        audio_stream = eleven_client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
            model_id="eleven_monolingual_v1",
            text=text
        )

        # convert stream → bytes safely
        audio_bytes = b"".join(chunk for chunk in audio_stream if chunk)

        return audio_bytes

    except Exception as e:
        print("❌ TTS ERROR:", str(e))
        return None