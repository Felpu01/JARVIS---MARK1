from modules.alerts import push_event
from core.action_system import execute_external_action

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

    # 🟢 DEFAULT FLOW
    return {
        "action": "respond",
        "priority": "low",
        "reason": "default_flow"
    }


# =========================
# EXECUTION LAYER
# =========================

def execute_decision(decision, message):

    action = decision["action"]

    # 🔴 ALERT SYSTEM (internal + external)
    if action == "alert":

        # internal event
        push_event(f"ALERT: {message}", decision["priority"])

        # external execution (Telegram / future tools)
        execute_external_action("telegram", {
            "message": f"🚨 MARK34 ALERT: {message}"
        })

        return {
            "status": "alert_triggered",
            "external": "telegram_sent"
        }

    # 🟡 TASK STORAGE
    if action == "store_task":
        push_event(f"TASK: {message}", decision["priority"])

        return {
            "stored": True,
            "message": "Task registered"
        }

    # 🔵 RESPONSE
    if action == "respond":
        return {
            "response": f"Procesado: {message}"
        }

    return {
        "response": "No action taken",
        "status": "unknown_action"
    }
