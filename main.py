from flask import Flask, request, jsonify
import os
import json
import time
from supabase import create_client

app = Flask(__name__)

# 🔐 SUPABASE (MEMORIA CENTRAL)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Supabase init error:", e)


# 📦 LOCAL CACHE MEMORY
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
        "last_goal": None,
        "last_action": None,
        "last_tool": None
    }


memory = load_memory()


def save_memory():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except:
        pass


# 🧠 INTENT ENGINE
def detect_intent(message):
    msg = message.lower()

    if "quiero" in msg:
        return "goal"

    if any(x in msg for x in ["qué recuerdas", "qué dijiste", "memoria"]):
        return "memory"

    if any(x in msg for x in ["ejecuta", "run", "analiza"]):
        return "execute"

    if any(x in msg for x in ["status", "estado"]):
        return "status"

    return "chat"


# 🧠 TOOL SYSTEM (REAL CORE)
def tool_router(task):
    task = task.lower()

    # 🧠 análisis
    if "analizar" in task:
        return "analyze", f"Analyzing: {task}"

    # 🧠 memoria
    if "recordar" in task or "memoria" in task:
        return "memory", f"Fetching memory for: {task}"

    # 🧠 simulación
    if "simular" in task:
        return "simulate", f"Simulating: {task}"

    # 🧠 default
    return "log", f"Processing: {task}"


# 🧠 SUPABASE MEMORY WRITE
def save_to_supabase(role, content):
    if not supabase:
        return

    try:
        supabase.table("memory").insert({
            "user_id": memory["user"],
            "type": role,
            "content": content,
            "timestamp": int(time.time())
        }).execute()

    except Exception as e:
        print("Supabase error:", e)


# 🧠 SUPABASE MEMORY READ (CEREBRO)
def get_memory(query=None):
    if not supabase:
        return []

    try:
        res = supabase.table("memory") \
            .select("*") \
            .eq("user_id", memory["user"]) \
            .order("id", desc=True) \
            .limit(20) \
            .execute()

        data = res.data[::-1]

        if query:
            return [d for d in data if query.lower() in d["content"].lower()]

        return data

    except Exception as e:
        print("Supabase read error:", e)
        return []


# 🧠 GOAL ENGINE
def create_goal(message):
    return message


# 🧠 EXECUTION DECISION ENGINE
def execute_task(message):
    tool, result = tool_router(message)

    memory["last_tool"] = tool
    memory["last_action"] = result

    # ejecutar tool
    if tool == "memory":
        cloud = get_memory(message)
        return f"🧠 MEMORY RESULT:\n" + "\n".join([c["content"] for c in cloud[-5:]])

    return f"🧠 TOOL: {tool}\nRESULT: {result}"


# 🧠 JARVIS CORE (MARK22)
def jarvis_response(message):
    intent = detect_intent(message)

    memory["history"].append(message)

    # 🎯 GOAL
    if intent == "goal":
        goal = create_goal(message)
        memory["goals"].append(goal)
        memory["last_goal"] = goal

        save_to_supabase("goal", goal)

        return f"🧠 GOAL REGISTERED:\n{goal}"

    # ⚙️ EXECUTE
    if intent == "execute":
        result = execute_task(message)

        save_to_supabase("execution", message)
        return result

    # 📊 STATUS
    if intent == "status":
        return (
            "🧠 MARK22 STATUS\n"
            f"Goals: {len(memory['goals'])}\n"
            f"Last tool: {memory['last_tool']}\n"
            f"Last action: {memory['last_action']}"
        )

    # 🧠 MEMORY QUERY
    if intent == "memory":
        cloud = get_memory()
        return "🧠 CLOUD MEMORY:\n" + "\n".join([c["content"] for c in cloud[-5:]])

    # 💬 DEFAULT
    return "🧠 MARK22 READY — use: quiero / ejecuta / status / memoria"


# 🌐 ROUTES
@app.route("/")
def home():
    return "JARVIS MARK22 SYSTEM BRAIN ACTIVE"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "empty message"}), 400

    response = jarvis_response(message)

    save_memory()

    return jsonify({
        "response": response,
        "memory": memory
    })


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
