from flask import Flask, request, jsonify
import os
import json
import math
import time
import uuid
from supabase import create_client

app = Flask(__name__)

# =========================
# 🔐 SUPABASE INIT
# =========================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Supabase init error:", e)


# =========================
# 🧠 GLOBAL MEMORY (SYSTEM)
# =========================
SYSTEM_MEMORY = {
    "user": "Matias",
    "agents": {},   # 🧠 NEW MARK34
}


# =========================
# 🧠 AGENT CREATION
# =========================
def create_agent(task):
    agent_id = str(uuid.uuid4())

    SYSTEM_MEMORY["agents"][agent_id] = {
        "id": agent_id,
        "task": task,

        "history": [],
        "active_task": task,

        "vectors": {},
        "plan": [],
        "step_index": 0,

        "failures": [],
        "fix_attempts": 0,

        "status": "active",

        "stats": {
            "queries": 0,
            "tools": 0,
            "retrievals": 0,
            "fixes": 0
        }
    }

    return agent_id


# =========================
# 🧠 EMBEDDING (igual que MARK32)
# =========================
def embed(text):
    vec = {}
    for w in text.lower().split():
        vec[w] = vec.get(w, 0) + 1
    return vec


def similarity(a, b):
    keys = set(a.keys()).union(set(b.keys()))
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)

    mag_a = math.sqrt(sum(v*v for v in a.values()))
    mag_b = math.sqrt(sum(v*v for v in b.values()))

    if mag_a == 0 or mag_b == 0:
        return 0

    return dot / (mag_a * mag_b)


# =========================
# 🧠 AGENT PLANNER
# =========================
def planner(task):
    return [
        f"understand: {task}",
        f"decompose: {task}",
        "retrieve context",
        "select tool",
        "execute",
        "validate"
    ]


# =========================
# ⚙️ TOOL SYSTEM
# =========================
def tool_router(step):
    step = step.lower()

    if "analizar" in step:
        return "analyze", f"Analyzing {step}"

    if "buscar" in step:
        return "search", f"Searching {step}"

    if "validar" in step:
        return "validate", f"Validating {step}"

    return "think", f"Processing {step}"


def execute(step):
    tool, result = tool_router(step)

    if "error" in step:
        return False, result + " (FAIL)"

    return True, result + " (OK)"


# =========================
# 🧠 AGENT ENGINE
# =========================
def run_agent(agent):
    if not agent["plan"]:
        agent["plan"] = planner(agent["active_task"])
        agent["step_index"] = 0

    if agent["step_index"] >= len(agent["plan"]):
        agent["status"] = "completed"
        return f"✅ COMPLETED: {agent['task']}"

    step = agent["plan"][agent["step_index"]]
    agent["step_index"] += 1

    agent["history"].append(step)

    success, result = execute(step)

    if not success:
        agent["failures"].append(step)
        agent["fix_attempts"] += 1

    return {
        "agent_id": agent["id"],
        "step": step,
        "result": result,
        "status": agent["status"]
    }


# =========================
# 🚀 START AGENT
# =========================
@app.route("/agent/start", methods=["POST"])
def start_agent():
    data = request.json or {}
    task = data.get("task", "default task")

    agent_id = create_agent(task)

    return jsonify({
        "agent_id": agent_id,
        "status": "created"
    })


# =========================
# 💬 RUN AGENT STEP
# =========================
@app.route("/agent/run", methods=["POST"])
def agent_run():
    data = request.json or {}
    agent_id = data.get("agent_id")

    if agent_id not in SYSTEM_MEMORY["agents"]:
        return jsonify({"error": "invalid agent"}), 400

    agent = SYSTEM_MEMORY["agents"][agent_id]

    result = run_agent(agent)

    return jsonify(result)


# =========================
# 🧠 AGENT STATE
# =========================
@app.route("/agent/state", methods=["GET"])
def agent_state():
    agent_id = request.args.get("agent_id")

    if agent_id not in SYSTEM_MEMORY["agents"]:
        return jsonify({"error": "invalid agent"}), 400

    return jsonify(SYSTEM_MEMORY["agents"][agent_id])


# =========================
# 🌐 HOME
# =========================
@app.route("/")
def home():
    return "JARVIS MARK34 MULTI-AGENT SYSTEM ACTIVE"


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
