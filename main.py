from flask import Flask, request, jsonify
import os
import json
from supabase import create_client

app = Flask(__name__)

# 🔐 SUPABASE
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
        "goals": [],
        "steps_executed": 0,
        "stats": {
            "messages": 0,
            "tools_used": 0
        }
    }


memory = load_memory()


def save_memory():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except:
        pass


# 🧠 INTENT
def detect_intent(message):
    msg = message.lower()

    if any(x in msg for x in ["hola", "buenas"]):
        return "greeting"

    if any(x in msg for x in ["status", "estado"]):
        return "status"

    if any(x in msg for x in ["calcula", "analiza", "plan", "automatiza", "crea"]):
        return "task"

    if any(x in msg for x in ["antes", "memoria", "dijiste"]):
        return "memory_query"

    return "general"


# 🧠 TOOL SET (MARK17)
def tool_executor(tool, payload):
    if tool == "calculator":
        try:
            return eval(payload["expression"])
        except:
            return "error"

    if tool == "analyzer":
        text = payload.get("text", "")
        return {
            "length": len(text),
            "words": len(text.split()),
            "complexity": "high" if len(text.split()) > 10 else "low"
        }

    if tool == "planner":
        task = payload.get("task", "")
        return [
            f"Definir objetivo: {task}",
            "Descomponer tarea",
            "Asignar subprocesos",
            "Ejecutar",
            "Validar resultado"
        ]

    return "unknown_tool"


# 🧠 TOOL ROUTER
def tool_router(message):
    msg = message.lower()

    if "calcula" in msg:
        return {"tool": "calculator", "payload": {"expression": msg.replace("calcula", "")}}

    if "analiza" in msg:
        return {"tool": "analyzer", "payload": {"text": message}}

    if "plan" in msg or "automatiza" in msg:
        return {"tool": "planner", "payload": {"task": message}}

    return None


# 🧠 MEMORY SEARCH SIMPLE
def search_memory(query):
    return [m for m in memory["history"] if query.lower() in m.lower()][-5:]


# 🧠 🧠 AUTONOMOUS PLANNER (NUEVO MARK17 CORE)
def autonomous_planner(message):
    """
    Genera un plan multi-step tipo agente autónomo
    """

    base_tool = tool_router(message)

    if not base_tool:
        return None

    tool_name = base_tool["tool"]

    # 🔥 TOOL CHAINING LOGIC
    if tool_name == "planner":
        return [
            {"tool": "analyzer", "payload": {"text": message}},
            {"tool": "planner", "payload": {"task": message}}
        ]

    if tool_name == "analyzer":
        return [
            {"tool": "analyzer", "payload": {"text": message}}
        ]

    if tool_name == "calculator":
        return [
            {"tool": "calculator", "payload": base_tool["payload"]}
        ]

    return None


# 🧠 EXECUTION ENGINE (CHAIN RUNNER)
def execute_chain(chain):
    results = []

    for step in chain:
        tool = step["tool"]
        payload = step["payload"]

        result = tool_executor(tool, payload)

        memory["stats"]["tools_used"] += 1

        results.append({
            "tool": tool,
            "result": result
        })

    return results


# 🧠 AGENT CORE MARK17
def jarvis_response(message):
    msg = message.lower()
    memory["stats"]["messages"] += 1

    intent = detect_intent(message)

    # 🧠 MEMORY QUERY
    if intent == "memory_query":
        results = search_memory(msg)
        return "🧠 MEMORY:\n" + "\n".join(results) if results else "Sin datos."

    # 🧠 AUTONOMOUS CHAIN
    chain = autonomous_planner(message)

    if chain:
        results = execute_chain(chain)

        return (
            "🧠 AUTONOMOUS EXECUTION\n"
            + "\n".join(
                f"{r['tool']} -> {r['result']}"
                for r in results
            )
        )

    # 🔥 BASE RESPONSES
    if intent == "greeting":
        return "🧠 MARK17 AUTONOMOUS AGENT ONLINE"

    if intent == "status":
        return f"OK | msgs:{memory['stats']['messages']} | tools:{memory['stats']['tools_used']}"

    return f"🧠 INPUT PROCESSED: {message}"


# 🌐 ROUTES
@app.route("/")
def home():
    return "JARVIS MARK17 AUTONOMOUS AGENT ACTIVE"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "empty message"}), 400

    memory["history"].append(message)

    response = jarvis_response(message)

    memory["steps_executed"] += 1

    save_memory()

    return jsonify({
        "response": response,
        "memory": memory
    })


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
