from flask import Flask, request, jsonify
import os
import json
import time
from supabase import create_client

app = Flask(__name__)

# 🔐 SUPABASE (MEMORIA EXTERNA)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Supabase init error:", e)


# 📦 MEMORY LOCAL CACHE
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

        # 🧠 SEMANTIC CORE
        "knowledge": [],
        "embeddings_fake": {},

        # 🧠 REASONING STATE
        "active_task": None,
        "plan": [],
        "step_index": 0,

        # 🧠 SELF IMPROVEMENT
        "reflections": [],
        "score": 0,

        # 📊 STATS
        "stats": {
            "queries": 0,
            "reasoning_cycles": 0,
            "improvements": 0
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

    if "por qué" in msg or "cómo" in msg:
        return "reason"

    if "ejecuta" in msg:
        return "run"

    if "memoria" in msg:
        return "memory"

    return "chat"


# 🧠 SEMANTIC SCORING (SIMULADO EMBEDDING SYSTEM)
def semantic_score(query, text):
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())

    if not query_words:
        return 0

    overlap = len(query_words.intersection(text_words))
    return overlap / len(query_words)


# 🧠 SEMANTIC RETRIEVAL ENGINE
def retrieve_memory(query):
    if not supabase:
        return []

    try:
        res = supabase.table("memory") \
            .select("*") \
            .eq("user_id", memory["user"]) \
            .order("id", desc=True) \
            .limit(50) \
            .execute()

        data = res.data[::-1]

        scored = []

        for item in data:
            score = semantic_score(query, item["content"])
            scored.append((score, item["content"]))

        scored.sort(reverse=True, key=lambda x: x[0])

        return [s[1] for s in scored[:5]]

    except:
        return []


# 🧠 PLANNER (HIERARCHICAL)
def planner(task):
    return {
        "goal": task,
        "subtasks": [
            f"Analizar contexto de: {task}",
            "Buscar información relevante",
            "Diseñar estrategia",
            "Ejecutar solución",
            "Validar resultado"
        ]
    }


# ⚙️ EXECUTOR
def execute(step):
    if "error" in step.lower():
        return False, "FAIL"

    return True, f"OK: {step}"


# 🔍 REFLECTOR (SELF IMPROVEMENT CORE)
def reflect(step, result):
    score = semantic_score(step, result)

    memory["score"] = score
    memory["reflections"].append({
        "step": step,
        "result": result,
        "score": score
    })

    if score < 0.2:
        return "IMPROVE"

    return "OK"


# 🧠 REASONING ENGINE (MARK25 CORE)
def reasoning_engine(query):
    memory["stats"]["reasoning_cycles"] += 1

    context = retrieve_memory(query)

    plan = planner(query)

    reasoning_output = {
        "query": query,
        "context": context,
        "plan": plan,
        "decision": None
    }

    if len(context) > 0:
        reasoning_output["decision"] = "USE_MEMORY_CONTEXT"
    else:
        reasoning_output["decision"] = "FRESH_REASONING"

    return reasoning_output


# 🧠 AGENT CYCLE
def agent_cycle():
    if not memory["active_task"]:
        return "No active task"

    if not memory["plan"]:
        memory["plan"] = planner(memory["active_task"])["subtasks"]
        memory["step_index"] = 0

    if memory["step_index"] >= len(memory["plan"]):
        task = memory["active_task"]
        memory["active_task"] = None
        memory["plan"] = []
        return f"Task completed: {task}"

    step = memory["plan"][memory["step_index"]]
    memory["step_index"] += 1

    success, result = execute(step)

    decision = reflect(step, result)

    if decision == "IMPROVE":
        memory["stats"]["improvements"] += 1
        memory["plan"] = planner(memory["active_task"])["subtasks"]
        memory["step_index"] = 0

        return f"🔁 Self-improvement triggered on: {step}"

    return f"STEP: {step} -> {result}"


# 🧠 MAIN ENGINE
def jarvis_response(message):
    intent = detect_intent(message)

    memory["history"].append(message)
    memory["stats"]["queries"] += 1

    # 🎯 TASK
    if intent == "task":
        memory["active_task"] = message
        return f"🧠 TASK SET:\n{message}"

    # ⚙️ RUN
    if intent == "run":
        return agent_cycle()

    # 🧠 REASONING
    if intent == "reason":
        result = reasoning_engine(message)
        return json.dumps(result, indent=2)

    # 🧠 MEMORY QUERY
    if intent == "memory":
        return "🧠 SEMANTIC MEMORY:\n" + "\n".join(retrieve_memory(message))

    return "🧠 MARK25 READY — task / ejecuta / por qué / memoria"


# 🌐 ROUTES
@app.route("/")
def home():
    return "JARVIS MARK25 SEMANTIC REASONING ENGINE ACTIVE"


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
