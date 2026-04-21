def plan_actions(message: str):
    msg = message.lower()

    actions = []

    # navigation
    if "open" in msg and "document" in msg:
        actions.append({
            "action": "OPEN_PAGE",
            "target": "documents"
        })

    # settings
    if "go to settings" in msg:
        actions.append({
            "action": "OPEN_PAGE",
            "target": "settings"
        })

    # fill form example
    if "change my name to" in msg:
        name = msg.split("to")[-1].strip()
        actions.append({
            "action": "FILL_INPUT",
            "field": "name",
            "value": name
        })

    return actions