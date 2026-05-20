from memory.memory import get_memory
from modules.alerts import push_event

# =========================
# DECISION ENGINE
# =========================

def decide(message, category):

    msg = message.lower()

    # 🔴 HIGH PRIORITY EVENTS
    if "error" in msg or "urgente" in msg:
        return {
            "action": "alert",
            "priority": "high",
            "reason": "critical_keyword"
        }

    # 🟡 TASK CREATION
    if category == "task":
        return {
            "action": "store_task",
            "priority": "medium",
            "reason": "user_request"
        }

    # 🔵 STATUS CHECK
    if "estado" in msg:
        return {
            "action": "respond",
            "priority": "low",
            "reason": "status_query"
        }

    # 🟢 DEFAULT
    return {
        "action": "respond",
        "priority": "low",
        "reason": "default_flow"
    }


def execute_decision(decision, message):

    action = decision["action"]

    if action == "alert":
        return push_event(f"ALERT: {message}", decision["priority"])

    if action == "store_task":
        return {
            "stored": True,
            "message": "Task registered"
        }

    if action == "respond":
        return {
            "response": f"Procesado: {message}"
        }

    return {"response": "No action taken"}
