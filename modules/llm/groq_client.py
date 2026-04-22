import requests
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def groq_generate(prompt):
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY missing")
        return None

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": os.getenv("GROQ_MODEL"),
                "messages": [
                    {"role": "system", "content": "You are Indra AI."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=15
        )

        if res.status_code != 200:
            print("❌ GROQ STATUS:", res.status_code, res.text)
            return None

        data = res.json()

        if "choices" not in data:
            print("❌ GROQ BAD RESPONSE:", data)
            return None

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("❌ GROQ ERROR:", e)
        return None