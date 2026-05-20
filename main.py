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

        # 🧠 CORE
        "history": [],
        "tasks": [],

        # 🧠 PLANNING SYSTEM
        "current_task": None,
        "plan": [],
        "step_index": 0,

        # 🧠 RESULTS
        "last_step": None,
        "last_result": None,

        # 📊 STATS
        "stats": {
            "plans": 0,
            "steps": 0,
            "fixes": 0
        }
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
        return "task"

    if "ejecuta" in msg or "continúa" in msg:
        return "run"

    if "status" in msg:
        return "status"

    return "chat"


# 🧠 PLANNER (MARK23 CORE)
def planner(task):
    return [
        f"Analizar objetivo: {task}",
        "Definir enfoque",
        "Construir estructura",
        "Implementar lógica base",
        "Ejecutar prueba",
        "Optimizar resultado"
    ]


# 🧠 EXECUTOR
def executor(step):
    if "error" in step.lower():
        return False, "FAIL"

    return True, f"OK: {step}"


# 🧠 REFLECTOR (EVALUADOR)
def reflect(success, step):
    if not success:
        memory["stats"]["fixes"] += 1
        return "RETRY_REQUIRED"
    return "OK"


# 🧠 NEXT STEP
def next_step():
    if memory["step_index"] >= len(memory["plan"]):
        return None

    step = memory["plan"][memory["step_index"]]
    memory["step_index"] += 1
    return step


# 🧠 AGENT LOOP (CORE MARK23)
def agent_loop():
    if not memory["current_task"]:
        return "No active task"

    # 🧠 create plan if not exists
    if not memory["plan"]:
        memory["plan"] = planner(memory["current_task"])
        memory["step_index"] = 0
        memory["stats"]["plans"] += 1

    step = next_step()

    if not step:
        finished_task = memory["current_task"]
        memory["current_task"] = None
        memory["plan"] = []
        memory["step_index"] = 0
        return f"Task completed: {finished_task}"

    success, result = executor(step)

    decision = reflect(success, step)

    memory["last_step"] = step
    memory["last_result"] = result
    memory["stats"]["steps"] += 1

    if decision == "RETRY_REQUIRED":
        memory["plan"] = planner(memory["current_task"])
        memory["step_index"] = 0
        return f"⚠️ Retry triggered on: {step}"

    return f"Step executed: {step} -> {result}"


# 🧠 JARVIS CORE (MARK23)
def jarvis_response(message):
    intent = detect_intent(message)

    memory["history"].append(message)

    # 🎯 TASK CREATION
    if intent == "task":
        memory["current_task"] = message

        return (
            "🧠 TASK REGISTERED\n"
            f"{message}\n"
            "Use 'ejecuta' to start execution loop"
        )

    # ⚙️ RUN LOOP
    if intent == "run":
        return agent_loop()

    # 📊 STATUS
    if intent == "status":
        return (
            "🧠 MARK23 STATUS\n"
            f"Task: {memory['current_task']}\n"
            f"Plan steps: {len(memory['plan'])}\n"
            f"Current index: {memory['step_index']}\n"
            f"Last step: {memory['last_step']}"
        )

    # 💬 DEFAULT
    return (
        "🧠 MARK23 AGENT READY\n"
        "Commands:\n"
        "- quiero X\n"
        "- ejecuta\n"
        "- status"
    )


# 🌐 ROUTES
@app.route("/")
def home():
    return "JARVIS MARK23 PLANNER-EXECUTOR ACTIVE"


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
