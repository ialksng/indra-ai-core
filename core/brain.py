from core.lite import lite_response
from modules.llm.groq_client import groq_generate
from modules.llm.hf_client import generate_text
from core.planner import create_plan

import time


def chat(user_id, message, mode="lite", agent=False):

    if mode == "lite":
        response = lite_response(message)

    elif mode in ["smart", "ultra"]:
        response = None

        # 🔥 STEP 1 — Groq (primary)
        response = groq_generate(message)

        # 🔁 STEP 2 — retry Groq once
        if not response:
            print("⚠️ Groq retry...")
            time.sleep(1)
            response = groq_generate(message)

        # 🔄 STEP 3 — HF fallback
        if not response:
            print("⚠️ Switching to HF...")
            response = generate_text(message)

        # 🔁 STEP 4 — retry HF (for cold start)
        if not response:
            print("⚠️ HF retry (model loading)...")
            time.sleep(2)
            response = generate_text(message)

        # ❌ STEP 5 — final fallback
        if not response:
            response = "AI is temporarily unavailable. Please try again."

    else:
        response = "Invalid mode"

    actions = create_plan(message) if agent else []

    return {
        "message": response,
        "actions": actions
    }