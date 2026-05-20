from flask import Flask, request, jsonify
import os
import json
import math
import time
from supabase import create_client

app = Flask(__name__)

# ─────────────────────────────
# 🔐 SUPABASE
# ─────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        pass


# ─────────────────────────────
# 📦 MEMORY
# ─────────────────────────────
MEMORY_FILE = "memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)

    return {
        "user": "Matias",
        "history": [],
        "vectors": {},
        "debates": []
    }


memory = load_memory()


def save_memory():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except:
        pass


# ─────────────────────────────
# 🧠 EMBEDDING SIMPLE
# ─────────────────────────────
def embed(text):
    return {w: text.lower().split().count(w) for w in set(text.lower().split())}


def similarity(a, b):
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    mag_a = math.sqrt(sum(v*v for v in a.values()))
    mag_b = math.sqrt(sum(v*v for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0
    return dot / (mag_a * mag_b)


# ─────────────────────────────
# 🧠 MEMORY
# ─────────────────────────────
def store(text):
    memory["vectors"][text] = embed(text)


def retrieve(query):
    qv = embed(query)
    scored = []

    for text, vec in memory["vectors"].items():
        scored.append((similarity(qv, vec), text))

    scored.sort(reverse=True)
    return [t for _, t in scored[:5]]


# ─────────────────────────────
# 🧠 AGENTES PLANNERS
# ─────────────────────────────
def planner_a(task):
    return [f"deep analysis of {task}", "step breakdown", "validate logic"]

def planner_b(task):
    return [f"fast execution {task}", "direct solve", "return result"]

def planner_c(task):
    return [f"structural approach {task}", "memory retrieval", "step execution"]


# ─────────────────────────────
# 🗣️ DEBATE SYSTEM (MARK30 CORE)
# ─────────────────────────────
def debate(task):
    plans = {
        "A": planner_a(task),
        "B": planner_b(task),
        "C": planner_c(task)
    }

    arguments = []

    # 🧠 cada agente critica a los otros
    for name, plan in plans.items():
        score = 0

        if len(plan) >= 3:
            score += 1

        if "fast" in plan[0]:
            score -= 0.2  # rápido pero menos preciso

        if "deep" in plan[0]:
            score += 0.3  # más calidad

        arguments.append((score, name, plan))

    arguments.sort(reverse=True)

    best_score, best_name, best_plan = arguments[0]

    memory["debates"].append({
        "task": task,
        "winner": best_name,
        "score": best_score,
        "all": arguments
    })

    return best_plan, {
        "winner": best_name,
        "score": best_score,
        "arguments": arguments
    }


# ─────────────────────────────
# ⚙️ EXECUTION
# ─────────────────────────────
def execute(step):
    if "error" in step:
        return False, f"{step} FAIL"
    return True, f"{step} OK"


# ─────────────────────────────
# 🧪 CRITIC
# ─────────────────────────────
def critic(step, result):
    score = 0
    if result:
        score += 0.5
    if "fail" not in result:
        score += 0.3
    if len(result) > 5:
        score += 0.2

    return score >= 0.7


# ─────────────────────────────
# 🔁 ORCHESTRATOR
# ─────────────────────────────
def run_cycle(task):
    plan, meta = debate(task)

    logs = []
    results = []

    context = retrieve(task)

    for step in plan:
        success, result = execute(step)
        ok = critic(step, result)

        logs.append({
            "step": step,
            "result": result,
            "ok": ok,
            "context": context
        })

        if not ok:
            fix = f"fix:{step}"
            _, fix_result = execute(fix)
            results.append(fix_result)
        else:
            results.append(result)

    return {
        "task": task,
        "debate": meta,
        "context": context,
        "results": results,
        "logs": logs
    }


# ─────────────────────────────
# 🧠 ROUTER
# ─────────────────────────────
def router(msg):
    msg = msg.lower()

    if "quiero" in msg:
        return "task"

    if "ejecuta" in msg:
        return "run"

    if "memoria" in msg:
        return "memory"

    return "chat"


# ─────────────────────────────
# 🧠 MAIN BRAIN
# ─────────────────────────────
def jarvis_response(message):
    memory["history"].append(message)
    store(message)

    mode = router(message)

    if mode == "task":
        return f"🧠 TASK REGISTERED: {message}"

    if mode == "run":
        return run_cycle(message)

    if mode == "memory":
        return retrieve(message)

    return "🧠 MARK30 ACTIVE — debate system online"


# ─────────────────────────────
# 🌐 API
# ─────────────────────────────
@app.route("/")
def home():
    return "JARVIS MARK30 DEBATE SYSTEM ACTIVE"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    msg = data.get("message", "")

    if not msg:
        return jsonify({"error": "empty"}), 400

    res = jarvis_response(msg)

    save_memory()

    return jsonify({
        "response": res,
        "memory": memory
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
