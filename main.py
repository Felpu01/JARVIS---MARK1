from flask import Flask, request, jsonify
import os
import json
import math
import time
from supabase import create_client

app = Flask(__name__)

# 🔐 SUPABASE
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
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)

    return {
        "user": "Matias",
        "history": [],
        "active_task": None,
        "vectors": {},
        "stats": {
            "queries": 0,
            "tools": 0,
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


# 🧠 EMBEDDING SIMPLE
def embed(text):
    vec = {}
    for w in text.lower().split():
        vec[w] = vec.get(w, 0) + 1
    return vec


def similarity(a, b):
    keys = set(a.keys()).union(set(b.keys()))
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    mag_a = math.sqrt(sum(v * v for v in a.values()))
    mag_b = math.sqrt(sum(v * v for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0
    return dot / (mag_a * mag_b)


# ☁️ SUPABASE EVENT LOG
def save_event(event_type, content):
    if not supabase:
        return
    try:
        supabase.table("memory").insert({
            "user_id": memory["user"],
            "type": event_type,
            "content": content,
            "timestamp": int(time.time())
        }).execute()
    except:
        pass


# 🧠 STORE MEMORY
def store_memory(text):
    memory["vectors"][text] = embed(text)
    save_event("vector", text)


# 🔍 RETRIEVAL
def retrieve(query):
    results = []
    qv = embed(query)

    for text, vec in memory["vectors"].items():
        score = similarity(qv, vec)
        results.append((score, text))

    results.sort(reverse=True, key=lambda x: x[0])
    return [r[1] for r in results[:5]]


# ─────────────────────────────────────────────
# 🧠 MARK29 — MULTI PLANNER SYSTEM
# ─────────────────────────────────────────────

def planner_a(task):
    return [
        f"deep analyze: {task}",
        "breakdown task",
        "validate logic"
    ]


def planner_b(task):
    return [
        f"fast solve: {task}",
        "execute directly",
        "return result"
    ]


def planner_c(task):
    return [
        f"structured plan: {task}",
        "retrieve memory",
        "execute step by step"
    ]


# ⚖️ VOTING SCORE
def score_plan(plan):
    score = 0
    if len(plan) >= 3:
        score += 0.3
    if any("validate" in p for p in plan):
        score += 0.3
    if any("memory" in p or "retrieve" in p for p in plan):
        score += 0.4
    return score


# 🧠 SELECT BEST PLAN (VOTING)
def select_best_plan(task):
    plans = {
        "A": planner_a(task),
        "B": planner_b(task),
        "C": planner_c(task),
    }

    scored = []

    for name, plan in plans.items():
        scored.append((score_plan(plan), name, plan))

    scored.sort(reverse=True, key=lambda x: x[0])

    best_score, best_name, best_plan = scored[0]

    return best_plan, {
        "selected": best_name,
        "score": best_score,
        "all": scored
    }


# ⚙️ EXECUTION ENGINE
def execute(step):
    if "error" in step.lower():
        return False, f"{step} FAILED"
    return True, f"{step} OK"


# 🧪 CRITIC AGENT
def critic(step, result):
    score = 0

    if result:
        score += 0.5
    if "fail" not in result.lower():
        score += 0.3
    if len(result) > 5:
        score += 0.2

    return {
        "score": score,
        "ok": score >= 0.75
    }


# 🔁 ORCHESTRATOR CORE
def run_cycle(task):
    plan, meta = select_best_plan(task)

    memory["active_task"] = task

    logs = []
    results = []

    for step in plan:
        context = retrieve(step)

        success, result = execute(step)
        evaluation = critic(step, result)

        logs.append({
            "step": step,
            "result": result,
            "context": context,
            "critic": evaluation
        })

        if not evaluation["ok"]:
            fix = f"fix:{step}"
            success, fix_result = execute(fix)

            logs.append({
                "step": fix,
                "result": fix_result,
                "context": context,
                "critic": "AUTO FIX"
            })

            results.append(fix_result)
            memory["stats"]["fixes"] += 1
        else:
            results.append(result)

    return {
        "task": task,
        "planner": meta,
        "results": results,
        "logs": logs
    }


# 🧠 ROUTER
def router(message):
    msg = message.lower()

    if "quiero" in msg:
        return "task"

    if "ejecuta" in msg:
        return "run"

    if "memoria" in msg:
        return "memory"

    return "chat"


# 🧠 MAIN BRAIN
def jarvis_response(message):
    memory["history"].append(message)
    memory["stats"]["queries"] += 1

    store_memory(message)
    save_event("message", message)

    mode = router(message)

    if mode == "task":
        memory["active_task"] = message
        return f"🧠 TASK SET: {message}"

    if mode == "run":
        if not memory["active_task"]:
            return "No active task"
        return run_cycle(memory["active_task"])

    if mode == "memory":
        return retrieve(message)

    return "🧠 MARK29 ACTIVE — listo para task / run / memory"


# 🌐 API
@app.route("/")
def home():
    return "JARVIS MARK29 MULTI-AGENT ACTIVE"


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
