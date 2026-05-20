from app import app
import threading
import time

from core.autonomy import autonomy_loop
from core.brain import brain

# =========================
# LIGHTWEIGHT LOCAL HOOKS
# (solo runtime helpers)
# =========================

def push_to_user(message, priority="low"):
    print(f"📡 PUSH [{priority}]: {message}")
    return {
        "message": message,
        "priority": priority,
        "timestamp": time.time()
    }

def speak(text):
    return text

# =========================
# ROUTE COMPATIBILITY LAYER
# (opcional bridge si lo necesitás)
# =========================

def process_message(message):
    return brain(message)

# =========================
# START SYSTEM
# =========================

if __name__ == "__main__":
    print("🧠 MARK34 STARTING...")

    threading.Thread(target=autonomy_loop, daemon=True).start()

    app.run(
        host="0.0.0.0",
        port=1000
    )
