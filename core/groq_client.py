import requests
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def groq_generate(prompt):
    if not GROQ_API_KEY:
        return None

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are Indra AI."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=15
        )

        data = res.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("GROQ ERROR:", e)
        return None