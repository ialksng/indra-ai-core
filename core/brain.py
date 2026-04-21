from core.lite import lite_response
from modules.llm.hf_client import generate_text
from modules.llm.groq_client import groq_generate
from core.planner import create_plan


def chat(user_id, message, mode="lite", agent=False):

    # 🔥 MODE HANDLING (clean upgrade)

    if mode == "lite":
        response = lite_response(message)

    elif mode == "smart":
        # try better model first
        response = groq_generate(message)

        if not response:
            response = generate_text(message)

        if not response:
            response = "AI unavailable"

    elif mode == "ultra":
        # for now same as smart (we upgrade later)
        response = groq_generate(message) or generate_text(message) or "AI unavailable"

    else:
        response = "Invalid mode"

    actions = create_plan(message) if agent else []

    return {
        "message": response,
        "actions": actions
    }