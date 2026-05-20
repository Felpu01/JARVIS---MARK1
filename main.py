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
    except:
        pass


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
            "commands": 0
        }
    }


memory = load_memory()


def save_memory():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except:
        pass


# 🧠 INTENT ENGINE (MARK16)
def detect_intent(message):
    msg = message.lower()

    if any(x in msg for x in ["hola", "buenas", "hey"]):
        return "greeting"

    if any(x in msg for x in ["cómo", "qué", "por qué", "explica"]):
        return "question"

    if any(x in msg for x in ["recordá", "guarda", "recuerda"]):
        return "command"

    if any(x in msg for x in ["estado", "status"]):
        return "status"

    if any(x in msg for x in ["antes", "memoria", "dijiste"]):
        return "memory_query"

    # 🧠 NEW: TOOL REQUEST
    if any(x in msg for x in ["crear", "calcular", "analizar", "plan", "ejecutar"]):
        return "tool_request"

    return "general"


# 🧠 PROFILE
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
    return [m for m in memory["history"] if query.lower() in m.lower()][-5:]


# 🧠 TOOLS SYSTEM (NUEVO MARK16 CORE)
def tool_executor(tool_name, payload):
    """
    Aquí nace el "agente real"
    """

    if tool_name == "calculator":
        try:
            return eval(payload["expression"])
        except:
            return "error"

    if tool_name == "summarize":
        text = payload.get("text", "")
        return text[:120] + "..."

    if tool_name == "planner":
        task = payload.get("task", "")
        return [
            f"Analizar: {task}",
            "Descomponer en pasos",
            "Ejecutar lógica",
            "Validar resultado"
        ]

    return "tool_not_found"


# 🧠 TOOL ROUTER (MARK16)
def tool_router(message):
    msg = message.lower()

    if "calcula" in msg:
        return {
            "tool": "calculator",
            "payload": {
                "expression": msg.replace("calcula", "").strip()
            }
        }

    if "resumir" in msg:
        return {
            "tool": "summarize",
            "payload": {
                "text": message
            }
        }

    if "planifica" in msg:
        return {
            "tool": "planner",
            "payload": {
                "task": message
            }
        }

    return None


# 🧠 JARVIS ENGINE MARK16
def jarvis_response(message):
    msg = message.lower()
    intent = detect_intent(message)

    memory["stats"]["messages"] += 1

    history = memory["history"]
    profile = memory["profile"]

    context = f"(Prev: '{history[-2]}')" if len(history) > 1 else ""

    # 🧠 TOOL SYSTEM (CORE MARK16)
    tool = tool_router(message)

    if tool:
        result = tool_executor(tool["tool"], tool["payload"])

        return (
            f"🧠 TOOL EXECUTED\n"
            f"Tool: {tool['tool']}\n"
            f"Result: {result}\n"
            f"Context: {context}"
        )

    # 🧠 MEMORY QUERY
    if intent == "memory_query":
        results = search_memory(msg)
        if results:
            return "🧠 MEMORY:\n" + "\n".join(f"- {r}" for r in results)
        return "Sin datos."

    # 🔥 BASE RESPONSES
    if intent == "greeting":
        return "🧠 MARK16 ONLINE"

    if intent == "status":
        return f"OK | msgs:{memory['stats']['messages']}"

    if intent == "question":
        return f"Procesando: '{message}'"

    if intent == "command":
        memory["stats"]["commands"] += 1
        return "Comando ejecutado"

    # 🧠 DEFAULT AGENT MODE
    return (
        f"🧠 AGENTE MARK16\n"
        f"Input: {message}\n"
        f"Context: {context}\n"
        f"Mode: ACTIVE"
    )


# 🌐 ROUTES
@app.route("/")
def home():
    return "JARVIS MARK16 TOOL AGENT ACTIVE"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "empty message"}), 400

    memory["history"].append(message)

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
