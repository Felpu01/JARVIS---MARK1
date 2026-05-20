import time

# =========================
# SIMPLE INTELLIGENCE LAYER
# =========================

def is_duplicate(new_item, existing_list):
    return new_item in existing_list[-20:]


def classify_message(message):
    msg = message.lower()

    if "recordá" in msg:
        return "task"

    if "revisar" in msg or "error" in msg:
        return "event"

    if "estado" in msg:
        return "status"

    return "info"


def should_store(message):
    # evita basura corta o irrelevante
    if len(message) < 3:
        return False
    return True


def summarize_history(history):
    if len(history) <= 10:
        return history
    return history[-10:]


def detect_user_pattern(history):
    patterns = {}

    for msg in history[-30:]:
        key = msg.lower()

        if "tarea" in key or "recordá" in key:
            patterns["task_user"] = patterns.get("task_user", 0) + 1

        if "estado" in key:
            patterns["status_checker"] = patterns.get("status_checker", 0) + 1

    return patterns
