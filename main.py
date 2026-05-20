from flask import Flask, request, jsonify
import os
import json
from supabase import create_client

app = Flask(__name__)

# 🔐 SUPABASE INIT (SAFE MODE)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# 📦 ARCHIVO LOCAL BACKUP
MEMORY_FILE = "memory.json"


# 🧠 LOAD MEMORY LOCAL
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)

    return {
        "user": "Matias",
        "history": [],
        "commands": [],
        "questions": [],
        "profile": {
            "role": None,
            "interests": [],
            "goals": []
        }
    }


# 💾 SAVE LOCAL MEMORY
def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


memory = load_memory()


# 🧠 INTENT DETECTOR
def detect_intent(message):
    msg = message.lower()

    if any(x in msg for x in ["hola", "buenas", "hey"]):
        return "greeting"

    if any(x in msg for x in ["quién", "qué es", "explica", "cómo", "por qué"]):
        return "question"

    if any(x in msg for x in ["recordá", "recuerda", "guarda"]):
        return "command"

    if any(x in msg for x in ["estado", "status"]):
        return "status"

    return "general"


# 🧠 PROFILE UPDATE (CONTROLADO)
def update_profile(message):
    msg = message.lower()

    if "soy" in msg:
        memory["profile"]["role"] = message

    if "me gusta" in msg or "me interesa" in msg:
        if message not in memory["profile"]["interests"]:
            memory["profile"]["interests"].append(message)

    if "quiero" in msg:
        if message not in memory["profile"]["goals"]:
            memory["profile"]["goals"].append(message)


# ☁️ SUPABASE SAVE (SAFE)
def save_to_supabase(message, response):
    if not supabase:
        return

    try:
        supabase.table("memory").insert({
            "user_id": memory["user"],
            "type": "message",
            "content": message
        }).execute()

        supabase.table("memory").insert({
            "user_id": memory["user"],
            "type": "response",
            "content": response
        }).execute()

    except Exception as e:
        print("Supabase error:", str(e))


# 🧠 JARVIS ENGINE
def jarvis_response(message):
    msg = message.lower()

    intent = detect_intent(message)

    history = memory["history"]
    profile = memory["profile"]

    context = f"(Antes dijiste '{history[-2]}')" if len(history) > 1 else ""

    # 🔥 BASE RESPONSES
    if intent == "greeting":
        return "Afirmativo. JARVIS en línea. ¿Cómo puedo asistirte?"

    if intent == "status":
        return "Todos los sistemas operativos. Sin anomalías detectadas."

    if intent == "question":
        return f"Analizando consulta: '{message}'. Procesamiento activo."

    if intent == "command":
        return f"Comando registrado: '{message}'. Ejecutando sistema."

    # 🧠 MEMORY MODE
    role = profile.get("role")
    interests = profile.get("interests", [])
    goals = profile.get("goals", [])

    if role or interests or goals:
        return (
            f"🧠 JARVIS MEMORY ACTIVE\n"
            f"Rol: {role}\n"
            f"Intereses: {interests}\n"
            f"Objetivos: {goals}\n\n"
            f"Procesado: '{message}' {context}"
        )

    return f"Afirmativo. He procesado: '{message}' {context}"


# 🌐 HOME
@app.route("/")
def home():
    return "JARVIS Core MARK8 activo"


# 💬 CHAT
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    # 🧠 LOCAL MEMORY
    memory["history"].append(message)

    if "recordá" in message.lower():
        memory["commands"].append(message)

    if any(x in message.lower() for x in ["qué", "cómo", "por qué"]):
        memory["questions"].append(message)

    # 🧠 PROFILE
    update_profile(message)

    # 🧠 RESPONSE
    response = jarvis_response(message)
    memory["last_response"] = response

    # 💾 SAVE LOCAL
    save_memory()

    # ☁️ SAVE CLOUD
    save_to_supabase(message, response)

    return jsonify({
        "response": response,
        "memory": memory
    })


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
