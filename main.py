from flask import Flask, request, jsonify
import os
import json
import time
import threading

app = Flask(__name__)

# =========================
# MEMORY
# =========================
memory = {
    "user": "Matias",
    "history": [],
    "tasks": [],
    "priority_events": [],
    "last_active": time.time(),
    "session_active": False
}

# =========================
# PUSH NOTIFICATION (HOOK)
# =========================
def push_to_user(message, priority="low"):
    event = {
        "message": message,
        "priority": priority,
        "timestamp": time.time()
    }

    memory["priority_events"].append(event)

    print("📡 PUSH:", message)

    return event

# =========================
# VOICE OUTPUT (HOOK)
# =========================
def speak(text):
    # luego conectás ElevenLabs / iOS TTS
    return text

# =========================
# PRIORITY ENGINE
# =========================
def decide_priority(message):
    msg = message.lower()

    if "urgente" in msg or "error" in msg:
        return "high"

    if "tarea" in msg or "recordá" in msg:
        return "medium"

    return "low"

# =========================
# JARVIS CORE BRAIN
# =========================
def brain(message):
    memory["history"].append(message)
    memory["last_active"] = time.time()
    memory["session_active"] = True

    priority = decide_priority(message)

    # 🔹 TASKS
    if "recordá" in message.lower():
        memory["tasks"].append(message)
        return speak("Tarea guardada.")

    # 🔹 STATUS
    if "estado" in message.lower():
        return speak("Sistema activo y estable.")

    # 🔹 SIMULATE EVENT DETECTION
    if "revisar" in message.lower():
        return push_to_user("Revisión requerida en sistema", priority)

    return speak(f"Procesado: {message}")

# =========================
# AUTONOMY ENGINE (LIVE)
# =========================
def autonomy_loop():
    while True:
        now = time.time()

        # 🧠 si está inactivo mucho tiempo
        if now - memory["last_active"] > 60:

            if memory["tasks"]:
                task = memory["tasks"][0]

                push_to_user(
                    f"Tienes tarea pendiente: {task}",
                    priority="medium"
                )

        # 🧹 cleanup
        if len(memory["history"]) > 100:
            memory["history"] = memory["history"][-30:]

        time.sleep(10)

# =========================
# VOICE SESSION MODE
# =========================
@app.route("/voice", methods=["POST"])
def voice():
    data = request.json or {}
    text = data.get("text", "")

    response = brain(text)

    return jsonify({
        "response": response,
        "session": True
    })

# =========================
# CHAT MODE
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")

    response = brain(message)

    return jsonify({
        "response": response,
        "memory": memory
    })

# =========================
# START
# =========================
if __name__ == "__main__":
    threading.Thread(target=autonomy_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
