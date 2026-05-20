def handle_alert(message):
    return {
        "event": "alert",
        "message": message,
        "priority": "high"
    }

def push_event(message, priority="low"):
    print(f"📡 EVENT [{priority}] {message}")
