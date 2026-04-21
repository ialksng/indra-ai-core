from modules.memory.store import search_memory
from modules.llm.fallback import generate_with_fallback
from core.router import is_complex
from core.planner import plan_actions

def chat(user_id, message):
    memory = search_memory(user_id, message)
    context = "\n".join(memory)

    prompt = f"""
You are Indra, a powerful personal AI assistant.

User memory:
{context}

User: {message}
Assistant:
"""

    use_external = is_complex(message)

    output = generate_with_fallback(prompt, use_external)

    response = output.split("Assistant:")[-1].strip()

    return {
        "type": "chat",
        "message": response,
        "actions": plan_actions(message)
    }