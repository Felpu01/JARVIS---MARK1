from flask import Flask, request, jsonify
import os
import json
import time
from supabase import create_client

app = Flask(__name__)

# 🔐 SUPABASE (KNOWLEDGE CORE)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Supabase init error:", e)


# 📦 MEMORY CACHE LOCAL
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
        "tasks": [],
        "active_task": None,

        # 🧠 AGENT STATE
        "plan": [],
        "step_index": 0,

        # 🧠 MULTI-AGENT FEEDBACK
        "last_step": None,
        "last_result": None,
        "critique": None,

        # 📊 STATS
        "stats": {
            "plans": 0,
            "steps": 0,
            "replans": 0
        }
    }


memory = load_memory()


def save_memory():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except:
        pass


# 🧠 TOOL SYSTEM (MARK24 CORE)
def tool_router(task):
    task = task.lower()

    if "analizar" in task:
        return "analyze", f"Analyzing: {task}"

    if "buscar" in task:
        return "search", f"Searching knowledge: {task}"

    if "simular" in task:
        return "simulate", f"Simulating: {task}"

    return "log", f"Processing: {task}"


# 🧠 SUPABASE MEMORY WRITE (KNOWLEDGE BASE)
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
    except:
        pass


# 🧠 SUPABASE READ (KNOWLEDGE RETRIEVAL)
def get_knowledge(query=None):
    if not supabase:
        return []

    try:
        res = supabase.table("memory") \
            .select("*") \
            .eq("user_id", memory["user"]) \
            .order("id", desc=True) \
            .limit(30) \
            .execute()

        data = res.data[::-1]

        if query:
            return [d for d in data if query.lower() in d["content"].lower()]

        return data

    except:
        return []


# 🧠 PLANNER AGENT
def planner_agent(task):
    return [
        f"Analizar: {task}",
        "Buscar contexto en memoria",
        "Definir estrategia",
        "Ejecutar implementación",
        "Validar resultado"
    ]


# ⚙️ EXECUTOR AGENT
def executor_agent(step):
    tool, result = tool_router(step)
    return tool, result


# 🔍 CRITIC AGENT (NUEVO MARK24 CORE)
def critic_agent(step, result):
    if "error" in result.lower():
        return "FAIL"
    if "unknown" in result.lower():
        return "WEAK"
    return "OK"


# 🧠 NEXT STEP
def next_step():
    if memory["step_index"] >= len(memory["plan"]):
        return None

    step = memory["plan"][memory["step_index"]]
    memory["step_index"] += 1
    return step


# 🧠 MULTI-AGENT LOOP (CORE MARK24)
def agent_cycle():
    if not memory["active_task"]:
        return "No active task"

    # 🧠 CREATE PLAN
    if not memory["plan"]:
        memory["plan"] = planner_agent(memory["active_task"])
        memory["step_index"] = 0
        memory["stats"]["plans"] += 1

    step = next_step()

    if not step:
        finished = memory["active_task"]
        memory["active_task"] = None
        memory["plan"] = []
        memory["step_index"] = 0

        return f"🧠 TASK COMPLETED: {finished}"

    # ⚙️ EXECUTE
    tool, result = executor_agent(step)

    # 🔍 CRITIQUE
    decision = critic_agent(step, result)

    memory["last_step"] = step
    memory["last_result"] = result
    memory["stats"]["steps"] += 1

    # ❌ FAIL → REPLAN
    if decision != "OK":
        memory["plan"] = planner_agent(memory["active_task"])
        memory["step_index"] = 0
        memory["stats"]["replans"] += 1

        return f"⚠️ REPLAN TRIGGERED ON: {step}"

    return f"STEP: {step} | TOOL: {tool} | RESULT: {result}"


# 🧠 JARVIS CORE (MARK24)
def jarvis_response(message):
    msg = message.lower()

    memory["history"].append(message)

    # 🎯 TASK CREATION
    if "quiero" in msg:
        memory["active_task"] = message
        save_to_supabase("task", message)

        return f"🧠 TASK SET:\n{message}\nUse 'ejecuta' to start agent cycle"

    # ⚙️ RUN CYCLE
    if "ejecuta" in msg:
        return agent_cycle()

    # 📊 STATUS
    if "status" in msg:
        return (
            "🧠 MARK24 STATUS\n"
            f"Task: {memory['active_task']}\n"
            f"Steps: {len(memory['plan'])}\n"
            f"Index: {memory['step_index']}\n"
            f"Last: {memory['last_result']}"
        )

    # 🧠 MEMORY QUERY
    if "memoria" in msg:
        data = get_knowledge()
        return "🧠 KNOWLEDGE BASE:\n" + "\n".join([d["content"] for d in data[-5:]])

    return "🧠 MARK24 READY — quiero / ejecuta / status / memoria"


# 🌐 ROUTES
@app.route("/")
def home():
    return "JARVIS MARK24 MULTI-AGENT OS ACTIVE"


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
