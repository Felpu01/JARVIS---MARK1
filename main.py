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
# MEMORY CORE
# =========================
memory = {
    "user": "Matias",
    "history": [],
    "tasks": [],
    "events": [],
    "last_active": time.time(),
    "conversation_mode": False
}

# =========================
# TEXT TO SPEECH (HOOK)
# =========================
def tts(text):
    """
    Después lo conectás a:
    - ElevenLabs API
    - iOS TTS
    - Amazon Polly
    """
    return text

# =========================
# SPEECH OUTPUT WRAPPER
# =========================
def speak(text):
    audio_text = tts(text)
    log("tts", text)
    return audio_text

# =========================
# LOGGING
# =========================
def log(event, content):
    if supabase:
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
# IPHONE BRIDGE (SHORTCUTS)
# =========================
def iphone_action(action, data):
    log("iphone_action", f"{action}:{data}")
    return {
        "action": action,
        "data": data
    }

# =========================
# JARVIS BRAIN (EVOLVED)
# =========================
def brain(message):
    msg = message.lower()
    memory["history"].append(message)
    memory["last_active"] = time.time()

    # activar modo conversación
    memory["conversation_mode"] = True

    log("message", message)

    # 🔹 BASIC RESPONSES
    if "hola" in msg:
        return speak("Estoy en línea. Listo para asistirte.")

    if "estado" in msg:
        return speak("Todos los sistemas operativos.")

    # 🔹 TASKS
    if "recordá" in msg:
        memory["tasks"].append(message)
        return speak("Tarea guardada.")

    if "tareas" in msg:
        return speak(f"Tienes {len(memory['tasks'])} tareas.")

    # 🔹 IPHONE COMMAND SIMULATION
    if "mensaje" in msg and "a" in msg:
        return iphone_action("send_message", message)

    return speak(f"He procesado: {message}")

# =========================
# AUTONOMY ENGINE (KEY DIFFERENCE)
# =========================
def autonomy_loop():
    while True:
        try:
            now = time.time()

            # 🧠 si está inactivo, puede hablar solo
            if now - memory["last_active"] > 120:

                if memory["tasks"]:
                    task = memory["tasks"][0]

                    event = f"Tienes una tarea pendiente: {task}"
                    memory["events"].append(event)

                    log("autonomy", event)

            # 🧹 cleanup
            if len(memory["history"]) > 100:
                memory["history"] = memory["history"][-30:]

            time.sleep(15)

        except Exception as e:
            print("autonomy error:", e)

# =========================
# VOICE INPUT ENDPOINT (FROM IPHONE)
# =========================
@app.route("/voice", methods=["POST"])
def voice():
    data = request.json or {}
    text = data.get("text", "")

    response = brain(text)

    return jsonify({
        "response": response,
        "voice_mode": True
    })

# =========================
# CHAT FALLBACK
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
# START SYSTEM
# =========================
if __name__ == "__main__":
    threading.Thread(target=autonomy_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
