import requests
import os

HF_API_KEY = os.getenv("HF_API_KEY")
HF_STT_MODEL = os.getenv("HF_STT_MODEL")

def speech_to_text(audio_bytes):
    if not HF_API_KEY:
        print("❌ HF_API_KEY missing")
        return None

    url = f"https://api-inference.huggingface.co/models/{HF_STT_MODEL}"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "audio/wav"
    }

    try:
        res = requests.post(url, headers=headers, data=audio_bytes)

        if res.status_code != 200:
            print("❌ STT ERROR:", res.text)
            return None

        data = res.json()
        return data.get("text")

    except Exception as e:
        print("❌ STT EXCEPTION:", e)
        return None