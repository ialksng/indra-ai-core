from gtts import gTTS
import os
import uuid

def text_to_speech(text):
    try:
        filename = f"/tmp/{uuid.uuid4()}.mp3"

        tts = gTTS(text=text, lang="en")
        tts.save(filename)

        return filename

    except Exception as e:
        print("❌ TTS ERROR:", e)
        return None