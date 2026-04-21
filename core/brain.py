from modules.llm.hf_client import generate_text
from core.planner import create_plan
from core.lite import lite_response

def chat(user_id, message, mode="lite", agent=False):

    if mode == "lite":
        response = lite_response(message)

    elif mode == "smart":
        response = generate_text(message)

    elif mode == "ultra":
        response = generate_text(message)

    else:
        response = "Invalid mode"

    actions = create_plan(message) if agent else []

    return {
        "message": response,
        "actions": actions
    }