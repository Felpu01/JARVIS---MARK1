from flask import Flask, request, jsonify
import os
import json
import math
import time
from supabase import create_client

app = Flask(__name__)

# 🔐 SUPABASE (MEMORIA GLOBAL)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Supabase init error:", e)


# 📦 LOCAL CACHE
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
        "active_task": None,

        # 🧠 VECTOR MEMORY
        "vectors": {},

        # 🧠 PLANNING
        "plan": [],
        "step_index": 0,

        # 🧠 SELF DEBUG
        "failures": [],
        "fix_attempts": 0,

        # 📊 STATS
        "stats": {
            "queries": 0,
            "tools": 0,
            "retrievals": 0,
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


# 🧠 EMBEDDING SIMULADO
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


# ☁️ SUPABASE WRITE
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


# 🧠 STORE VECTOR MEMORY
def store_memory(text):
    memory["vectors"][text] = embed(text)
    save_event("vector", text)


# 🔍 HYBRID RETRIEVAL (SQL + VECTOR)
def retrieve(query):
    results = []

    # 🧠 VECTOR SEARCH
    query_vec = embed(query)

    for text, vec in memory["vectors"].items():
        score = similarity(query_vec, vec)
        results.append((score, text))

    results.sort(reverse=True, key=lambda x: x[0])
    vector_results = [r[1] for r in results[:3]]

    # ☁️ SQL MEMORY SEARCH
    sql_results = []
    if supabase:
        try:
            res = supabase.table("memory") \
                .select("*") \
                .eq("user_id", memory["user"]) \
                .order("id", desc=True) \
                .limit(10) \
                .execute()

            for r in res.data:
                if query.lower() in r["content"].lower():
                    sql_results.append(r["content"])

        except:
            pass

    return list(set(vector_results + sql_results))[:5]


# 🧠 PLANNER (HIERARCHICAL)
def planner(task):
    return [
        f"understand: {task}",
        f"breakdown: {task}",
        "retrieve context",
        "select tool",
        "execute",
        "validate"
    ]


# ⚙️ TOOL SYSTEM
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

    memory["stats"]["tools"] += 1
    save_event("tool", f"{tool}:{result}")

    # 🧠 SIMULATED FAILURE
    if "error" in step.lower():
        return False, result + " (FAIL)"

    return True, result + " (OK)"


# 🔁 SELF DEBUG LOOP
def self_debug(step, result, success):
    if success:
        return "OK"

    memory["failures"].append({
        "step": step,
        "result": result
    })

    memory["fix_attempts"] += 1
    memory["stats"]["fixes"] += 1

    # 🔁 REPAIR LOGIC
    memory["plan"] = planner(memory["active_task"])
    memory["step_index"] = 0

    return "RETRY"


# 🔁 COGNITIVE ENGINE
def run_cycle():
    if not memory["active_task"]:
        return "No active task"

    if not memory["plan"]:
        memory["plan"] = planner(memory["active_task"])
        memory["step_index"] = 0

    if memory["step_index"] >= len(memory["plan"]):
        task = memory["active_task"]
        memory["active_task"] = None
        memory["plan"] = []
        return f"✅ COMPLETED: {task}"

    step = memory["plan"][memory["step_index"]]
    memory["step_index"] += 1

    context = retrieve(step)

    success, result = execute(step)

    decision = self_debug(step, result, success)

    return {
        "step": step,
        "tool_result": result,
        "context": context,
        "debug": decision
    }


# 🧠 MAIN BRAIN
def jarvis_response(message):
    msg = message.lower()

    memory["history"].append(message)
    memory["stats"]["queries"] += 1

    # 🧠 STORE EVERYTHING
    store_memory(message)
    save_event("message", message)

    # 🎯 TASK
    if "quiero" in msg:
        memory["active_task"] = message
        memory["plan"] = []
        return f"🧠 TASK SET: {message}"

    # ⚙️ RUN
    if "ejecuta" in msg:
        return run_cycle()

    # 🔍 MEMORY
    if "memoria" in msg:
        return retrieve(message)

    # ⚠️ FAIL TEST
    if "debug" in msg:
        return self_debug("test", "error simulated", False)

    return "🧠 MARK27 READY — quiero / ejecuta / memoria / debug"


# 🌐 API
@app.route("/")
def home():
    return "JARVIS MARK27 HYBRID AI SYSTEM ACTIVE"


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
