from flask import Flask, request, jsonify
import os
import json
import time
import threading
from supabase import create_client

app = Flask(__name__)

# =========================
# SUPABASE
# =========================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL else None

# =========================
# MEMORY
# =========================
memory = {
    "user": "Matias",
    "history": [],
    "tasks": [],
    "last_active": time.time(),
    "notifications": []
}

# =========================
# VOICE RESPONSE (TEXT ONLY HERE)
# =========================
def speak(text):
    # 👉 después lo conectás a TTS (ElevenLabs / iOS / etc)
    return text

# =========================
# SUPABASE LOG
# =========================
def log(event, content):
    if not supabase:
        return
    try:
        supabase.table("memory").insert({
            "user_id": memory["user"],
            "type": event,
            "content": content,
            "timestamp": int(time.time())
        }).execute()
    except:
        pass

# =========================
# JARVIS CORE BRAIN (tu MARK35 adaptado)
# =========================
def brain(message):
    msg = message.lower()
    memory["history"].append(message)
    memory["last_active"] = time.time()

    log("message", message)

    # --- COMMANDS ---
    if "hola" in msg:
        return speak("JARVIS online. Estoy activo.")

    if "estado" in msg:
        return speak("Todo el sistema funcionando correctamente.")

    if "recordá" in msg:
        memory["tasks"].append(message)
        return speak("Tarea registrada.")

    if "qué tengo" in msg:
        return speak(f"Tienes {len(memory['tasks'])} tareas activas.")

    return speak(f"Procesado: {message}")

# =========================
# AUTONOMY ENGINE (LO IMPORTANTE)
# =========================
def autonomy_loop():
    while True:
        try:
            now = time.time()

            # 🔁 inactivity check
            if now - memory["last_active"] > 60:
                if memory["tasks"]:
                    task = memory["tasks"][0]

                    notify = f"Tienes una tarea pendiente: {task}"
                    memory["notifications"].append(notify)

                    log("notification", notify)

            # 🧠 auto cleanup / memory maintenance
            if len(memory["history"]) > 50:
                memory["history"] = memory["history"][-20:]

            time.sleep(10)

        except Exception as e:
            print("autonomy error:", e)

# =========================
# IPHONE BRIDGE (SHORTCUTS LATER)
# =========================
def send_to_iphone(action, data):
    """
    Esto luego lo conectás con:
    - iOS Shortcuts webhook
    - o Pushcut / similar
    """
    log("iphone_action", f"{action}:{data}")

# =========================
# API
# =========================
@app.route("/")
def home():
    return "MARK36 JARVIS LIVE ACTIVE"

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
