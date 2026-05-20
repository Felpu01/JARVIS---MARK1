from flask import Flask, request, jsonify
import os
import json
from supabase import create_client

app = Flask(__name__)

# 🔐 SUPABASE INIT
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Supabase init error:", e)


# 📦 MEMORY FILE
MEMORY_FILE = "memory.json"


# 🧠 LOAD MEMORY
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            pass

    return {
        "user": "Matias",
        "history": [],
        "commands": [],
        "questions": [],
        "profile": {
            "role": None,
            "interests": [],
            "goals": []
        },
        "stats": {
            "messages": 0,
            "commands": 0,
            "memory_hits": 0
        }
    }


memory = load_memory()


# 💾 SAVE LOCAL
def save_memory():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print("Local save error:", e)


# 🧠 INTENT ENGINE
def detect_intent(message):
    msg = message.lower()

    if any(x in msg for x in ["hola", "buenas", "hey"]):
        return "greeting"

    if any(x in msg for x in ["quién", "qué es", "cómo", "por qué", "explica"]):
        return "question"

    if any(x in msg for x in ["recordá", "recuerda", "guarda"]):
        return "command"

    if any(x in msg for x in ["estado", "status"]):
        return "status"

    if any(x in msg for x in ["antes", "dijiste", "qué me", "recuerdo", "memoria"]):
        return "memory_query"

    return "general"


# 🧠 PROFILE ENGINE
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


# ☁️ SUPABASE WRITE
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
        print("Supabase error:", e)


# 🔍 LOCAL MEMORY SEARCH
def search_memory(query):
    query = query.lower()
    return [m for m in memory["history"] if query in m.lower()][-5:]


# ☁️ CLOUD MEMORY READ
def load_cloud_memory(limit=20):
    if not supabase:
        return []

    try:
        res = supabase.table("memory") \
            .select("*") \
            .eq("user_id", memory["user"]) \
            .order("id", desc=True) \
            .limit(limit) \
            .execute()

        return res.data[::-1]
    except:
        return []


# 🧠 AGENT CORE (MARK14)
def jarvis_response(message):
    msg = message.lower()
    intent = detect_intent(message)

    memory["stats"]["messages"] += 1

    history = memory["history"]
    profile = memory["profile"]

    local_context = f"(Local: '{history[-2]}')" if len(history) > 1 else ""

    cloud_memory = load_cloud_memory()

    cloud_msgs = [
        m["content"] for m in cloud_memory if m["type"] == "message"
    ][-5:]

    cloud_context = " | ".join(cloud_msgs)

    # 🧠 MEMORY AGENT MODE (NUEVO)
    if intent == "memory_query":
        memory["stats"]["memory_hits"] += 1

        local_hits = search_memory(msg)

        if local_hits:
            return "🧠 MEMORY LOCAL:\n" + "\n".join(f"- {x}" for x in local_hits)

        if cloud_context:
            return f"🧠 MEMORY CLOUD:\n{cloud_context}"

        return "No hay suficiente información en memoria."

    # 🔥 BASE AGENT RESPONSES
    if intent == "greeting":
        return "🧠 AGENTE ACTIVO. JARVIS en línea."

    if intent == "status":
        return f"OK | msgs:{memory['stats']['messages']} | mem_hits:{memory['stats']['memory_hits']}"

    if intent == "question":
        return f"Procesando lógica cognitiva: '{message}'"

    if intent == "command":
        memory["stats"]["commands"] += 1
        return f"Ejecutando acción: '{message}'"

    # 🧠 PERSONALITY ENGINE
    role = profile.get("role")
    interests = profile.get("interests", [])
    goals = profile.get("goals", [])

    if role or interests or goals:
        return (
            f"🧠 AGENTE COGNITIVO ACTIVO\n"
            f"Rol: {role}\n"
            f"Intereses: {interests}\n"
            f"Objetivos: {goals}\n\n"
            f"Procesado: '{message}' {local_context}"
        )

    return f"OK. Procesado: '{message}' {local_context}"


# 🌐 ROUTE
@app.route("/")
def home():
    return "JARVIS MARK14 AGENT ACTIVE"


# 💬 CHAT
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "empty message"}), 400

    memory["history"].append(message)

    if "recordá" in message.lower():
        memory["commands"].append(message)

    if any(x in message.lower() for x in ["qué", "cómo", "por qué"]):
        memory["questions"].append(message)

    update_profile(message)

    response = jarvis_response(message)
    memory["last_response"] = response

    save_memory()
    save_to_supabase(message, response)

    return jsonify({
        "response": response,
        "memory": memory
    })


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
