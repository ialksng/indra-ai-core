def is_complex(message: str):
    keywords = [
        "architecture",
        "build",
        "system",
        "design",
        "code",
        "optimize",
        "explain in detail"
    ]

    return any(k in message.lower() for k in keywords)