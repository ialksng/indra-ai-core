import requests
import os


def generate_text(prompt):
    HF_API_KEY = os.getenv("HF_API_KEY")
    HF_MODEL = os.getenv("HF_MODEL")
    HF_BASE_URL = os.getenv(
        "HF_BASE_URL",
        "https://api-inference.huggingface.co/models"
    )

    if not HF_API_KEY:
        print("❌ HF_API_KEY missing")
        return None

    if not HF_MODEL:
        print("❌ HF_MODEL missing")
        return None

    url = f"{HF_BASE_URL}/{HF_MODEL}"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(
            url,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": int(os.getenv("HF_MAX_TOKENS", 200)),
                    "temperature": float(os.getenv("HF_TEMPERATURE", 0.7)),
                    "return_full_text": False
                }
            },
            timeout=int(os.getenv("HF_TIMEOUT", 25))
        )

        # 🔥 handle non-200 safely
        if res.status_code != 200:
            print("❌ HF STATUS:", res.status_code, res.text)
            return None

        data = res.json()

        # 🔥 handle HF errors (model loading, etc.)
        if isinstance(data, dict) and "error" in data:
            print("❌ HF ERROR:", data["error"])
            return None

        # 🔥 normal response
        if isinstance(data, list) and len(data) > 0:
            if "generated_text" in data[0]:
                return data[0]["generated_text"].strip()

        print("❌ HF BAD RESPONSE:", data)
        return None

    except Exception as e:
        print("❌ HF EXCEPTION:", e)
        return None