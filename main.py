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


# 📦 LOCAL MEMORY FILE
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
        }
    }


memory = load_memory()


# 💾 SAVE LOCAL MEMORY
def save_memory():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print("Local save error:", e)


# 🧠 INTENT DETECTOR (MARK13)
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

    # 🧠 MEMORY QUERY (MEJORADO)
    if any(x in msg for x in ["antes", "dijiste", "recuerdas", "qué dije", "qué me dijiste"]):
        return "memory_query"

    return "general"


# 🧠 PROFILE UPDATE (ANTI DUPLICATES)
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
        print("Supabase error:", e)


# 🧠 LOCAL MEMORY SEARCH
def search_memory(query):
    query = query.lower()
    return [m for m in memory["history"] if query in m.lower()][-5:]


# ☁️ CLOUD MEMORY LOAD
def load_recent_memory(limit=20):
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
    except Exception as e:
        print("Supabase read error:", e)
        return []


# 🧠 JARVIS ENGINE (MARK13 FINAL)
def jarvis_response(message):
    msg = message.lower()
    intent = detect_intent(message)

    history = memory["history"]
    profile = memory["profile"]

    context = f"(Local: '{history[-2]}')" if len(history) > 1 else ""

    cloud_memory = load_recent_memory()

    cloud_context = ""
    if cloud_memory:
        last_msgs = [
            m["content"]
            for m in cloud_memory
            if m["type"] == "message"
        ][-5:]
        cloud_context = " | ".join(last_msgs)

    # 🧠 MEMORY QUERY ENGINE
    if intent == "memory_query":
        results = search_memory(msg)

        if results:
            return "🧠 RECUERDO ENCONTRADO:\n" + "\n".join(f"- {r}" for r in results)

        if cloud_context:
            return f"🧠 Recuerdo en nube:\n{cloud_context}"

        return "No tengo registros suficientes para eso."

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

    if role or interests or goals or cloud_context:
        return (
            f"🧠 JARVIS MEMORY ACTIVE\n"
            f"Rol: {role}\n"
            f"Intereses: {interests}\n"
            f"Objetivos: {goals}\n\n"
            f"Procesado: '{message}' {context}"
        )

    return f"Afirmativo. He procesado: '{message}' {context}"


# 🌐 HEALTH CHECK
@app.route("/")
def home():
    return "JARVIS MARK13 activo"


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
