import requests
import os

HF_API_KEY = os.getenv("HF_API_KEY")

API_URL = "https://api-inference.huggingface.co/models/distilgpt2"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

def generate_text(prompt):
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 100
                }
            },
            timeout=20
        )

        data = response.json()

        if isinstance(data, list):
            return data[0].get("generated_text", "No response")

        return "AI error"

    except Exception as e:
        print("HF ERROR:", e)
        return "AI unavailable"