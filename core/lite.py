def lite_response(message: str):
    msg = message.lower()

    if "hi" in msg or "hello" in msg:
        return "Hey 👋 How can I help you?"

    if "who are you" in msg:
        return "I'm Indra, your AI assistant."

    if "help" in msg:
        return "Try Smart mode for advanced answers."

    if "time" in msg:
        from datetime import datetime
        return f"Time: {datetime.now().strftime('%H:%M')}"

    return "Lite mode active. Switch to Smart for better responses."