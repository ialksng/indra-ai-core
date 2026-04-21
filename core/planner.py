def create_plan(message: str):
    msg = message.lower()
    actions = []

    if "open settings" in msg:
        actions.append({
            "action": "OPEN_PAGE",
            "target": "settings"
        })

    if "open documents" in msg:
        actions.append({
            "action": "OPEN_PAGE",
            "target": "documents"
        })

    if "change my name to" in msg:
        name = msg.split("to")[-1].strip()

        actions.extend([
            {"action": "OPEN_PAGE", "target": "settings"},
            {"action": "FILL_INPUT", "field": "name", "value": name},
            {"action": "SUBMIT_FORM"}
        ])

    return actions