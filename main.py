from flask import Flask, request, jsonify
import os
import json
import math

app = Flask(__name__)

# ─────────────────────────────
# 📦 MEMORY
# ─────────────────────────────
MEMORY_FILE = "memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)

    return {
        "history": [],
        "vectors": {},
        "reputation": {
            "A": 0.5,
            "B": 0.5,
            "C": 0.5
        },
        "agent_stats": {
            "A": {"wins": 0, "losses": 0},
            "B": {"wins": 0, "losses": 0},
            "C": {"wins": 0, "losses": 0}
        }
    }


memory = load_memory()


def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


# ─────────────────────────────
# 🧠 EMBEDDING SIMPLE
# ─────────────────────────────
def embed(text):
    return {w: text.lower().split().count(w) for w in set(text.lower().split())}


def similarity(a, b):
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    ma = math.sqrt(sum(v*v for v in a.values()))
    mb = math.sqrt(sum(v*v for v in b.values()))
    if ma == 0 or mb == 0:
        return 0
    return dot / (ma * mb)


# ─────────────────────────────
# 🧠 MEMORY STORE
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
# 🧠 AGENTES (con sesgo)
# ─────────────────────────────
def agent_a(task):
    return {
        "plan": [f"deep analysis: {task}", "structured breakdown", "validate"],
        "bias": 0.9  # preciso pero lento
    }


def agent_b(task):
    return {
        "plan": [f"fast solve: {task}", "direct execution", "return result"],
        "bias": 0.6  # rápido pero menos preciso
    }


def agent_c(task):
    return {
        "plan": [f"balanced approach: {task}", "memory retrieval", "step execution"],
        "bias": 0.75
    }


AGENTS = {
    "A": agent_a,
    "B": agent_b,
    "C": agent_c
}


# ─────────────────────────────
# ⚖️ SCORE + REPUTATION WEIGHTED
# ─────────────────────────────
def score_plan(plan, agent_id):
    base = 0

    if len(plan) >= 3:
        base += 1

    if "validate" in " ".join(plan):
        base += 0.5

    rep = memory["reputation"][agent_id]

    return base * rep


# ─────────────────────────────
# 🧠 DEBATE SYSTEM (MARK31 CORE)
# ─────────────────────────────
def debate(task):
    candidates = []

    for agent_id, agent_fn in AGENTS.items():
        out = agent_fn(task)

        plan = out["plan"]
        bias = out["bias"]

        score = score_plan(plan, agent_id)

        candidates.append({
            "agent": agent_id,
            "plan": plan,
            "score": score,
            "bias": bias
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)

    winner = candidates[0]

    # ─────────────────────────────
    # 🧬 EVOLUTION STEP
    # ─────────────────────────────
    for c in candidates:
        if c["agent"] == winner["agent"]:
            memory["reputation"][c["agent"]] += 0.02
            memory["agent_stats"][c["agent"]]["wins"] += 1
        else:
            memory["reputation"][c["agent"]] -= 0.01
            memory["agent_stats"][c["agent"]]["losses"] += 1

        # clamp
        memory["reputation"][c["agent"]] = max(
            0.1,
            min(1.5, memory["reputation"][c["agent"]])
        )

    return winner["plan"], {
        "winner": winner,
        "candidates": candidates,
        "reputation": memory["reputation"]
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
    if "fail" not in result.lower():
        score += 0.3
    if len(result) > 5:
        score += 0.2

    return score >= 0.7


# ─────────────────────────────
# 🔁 ORCHESTRATOR
# ─────────────────────────────
def run_cycle(task):
    plan, meta = debate(task)

    context = retrieve(task)

    logs = []
    results = []

    for step in plan:
        ok, result = execute(step)
        valid = critic(step, result)

        logs.append({
            "step": step,
            "result": result,
            "ok": valid
        })

        if not valid:
            ok2, fix = execute("fix:" + step)
            results.append(fix)
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

    return "🧠 MARK31 ACTIVE — agents evolve + reputation system online"


# ─────────────────────────────
# 🌐 API
# ─────────────────────────────
@app.route("/")
def home():
    return "JARVIS MARK31 EVOLUTION SYSTEM ACTIVE"


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
