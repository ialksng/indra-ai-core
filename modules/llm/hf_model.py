import requests
from config.settings import HF_API_KEY, HF_MODEL

API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

def hf_generate(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception("HF API failed")

    data = response.json()

    return data[0]["generated_text"]