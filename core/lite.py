def lite_response(message: str):
    msg = message.lower()

    if "hi" in msg or "hello" in msg:
        return "Hey 👋 How can I help you?"

    if "your name" in msg:
        return "I am Indra, your AI assistant."

    if "who are you" in msg:
        return "I'm Indra AI, designed to help you with tasks and automation."

    if "help" in msg:
        return "You can ask me to open pages, manage data, or answer questions."

    if "time" in msg:
        from datetime import datetime
        return f"Current time is {datetime.now().strftime('%H:%M')}"

    if "date" in msg:
        from datetime import datetime
        return f"Today's date is {datetime.now().strftime('%Y-%m-%d')}"

    return "I'm in lite mode. Switch to Smart for more advanced answers."