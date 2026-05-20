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


# 📦 MEMORY
MEMORY_FILE = "memory.json"


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

    if any(x in msg for x in ["antes", "dijiste", "memoria", "recuerdo"]):
        return "memory_query"

    # 🧠 MARK15 NEW: TASK INTENT
    if any(x in msg for x in ["haz", "crea", "arma", "construye", "planifica"]):
        return "task_request"

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


# ☁️ SUPABASE
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
    except:
        pass


# 🔍 MEMORY SEARCH
def search_memory(query):
    query = query.lower()
    return [m for m in memory["history"] if query in m.lower()][-5:]


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


# 🧠 🧠 THINKING ENGINE (NUEVO MARK15)
def thinking_step(message, profile, history):
    """
    Simula razonamiento interno del agente
    """

    goals = profile.get("goals", [])
    interests = profile.get("interests", [])

    context_score = len(history) + len(goals) + len(interests)

    if context_score > 10:
        return "HIGH_CONTEXT_MODE"
    elif context_score > 5:
        return "MEDIUM_CONTEXT_MODE"
    else:
        return "LOW_CONTEXT_MODE"


# 🧠 🧠 PLANNER ENGINE (NUEVO MARK15)
def planner(message):
    msg = message.lower()

    if "crear bot" in msg or "construir bot" in msg:
        return [
            "definir arquitectura",
            "seleccionar datos",
            "diseñar lógica",
            "implementar ejecución"
        ]

    if "automatizar" in msg:
        return [
            "identificar proceso",
            "mapear pasos",
            "crear flujo automático"
        ]

    if "analizar" in msg:
        return [
            "recolectar datos",
            "procesar información",
            "generar conclusión"
        ]

    return []


# 🧠 AGENT CORE MARK15
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

    # 🧠 THINKING LAYER (NUEVO)
    mode = thinking_step(message, profile, history)

    # 🧠 TASK PLANNER (NUEVO)
    plan = planner(message)

    # 🧠 MEMORY QUERY
    if intent == "memory_query":
        results = search_memory(msg)
        if results:
            return "🧠 MEMORY:\n" + "\n".join(f"- {r}" for r in results)
        return "No hay datos suficientes."

    # 🧠 TASK EXECUTION SIMULATION
    if intent == "task_request":
        if plan:
            return (
                "🧠 TASK PLAN GENERATED:\n"
                + "\n".join(f"{i+1}. {p}" for i, p in enumerate(plan))
                + f"\n\nMODE: {mode}"
            )

    # 🔥 BASE RESPONSES
    if intent == "greeting":
        return "🧠 AGENTE MARK15 ACTIVO"

    if intent == "status":
        return f"OK | msgs:{memory['stats']['messages']} | mode:{mode}"

    if intent == "question":
        return f"[{mode}] Procesando: '{message}'"

    if intent == "command":
        memory["stats"]["commands"] += 1
        return f"Ejecutando comando: '{message}'"

    # 🧠 MEMORY MODE
    role = profile.get("role")
    interests = profile.get("interests", [])
    goals = profile.get("goals", [])

    return (
        f"🧠 AGENTE MARK15\n"
        f"Modo: {mode}\n"
        f"Rol: {role}\n"
        f"Intereses: {interests}\n"
        f"Objetivos: {goals}\n"
        f"Contexto: {local_context}"
    )


# 🌐 ROUTES
@app.route("/")
def home():
    return "JARVIS MARK15 AGENT + PLANNER ACTIVE"


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
