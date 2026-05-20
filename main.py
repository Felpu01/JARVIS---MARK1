from flask import Flask, request, jsonify
import os
import json
import math
from supabase import create_client

app = Flask(__name__)

# 🔐 SUPABASE (MEMORY + EVENT STORE)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Supabase init error:", e)


# 📦 LOCAL MEMORY
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
        "embeddings": {},  # 🧠 VECTOR STORE SIMULADO

        "active_task": None,
        "plan": [],
        "step_index": 0,

        "tools_used": [],
        "reasoning_trace": [],

        "stats": {
            "queries": 0,
            "tool_calls": 0,
            "memory_hits": 0
        }
    }


memory = load_memory()


def save_memory():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except:
        pass


# 🧠 EMBEDDING SIMULADO (BASE VECTORIAL SIMPLE)
def embed(text):
    words = text.lower().split()
    vec = {}
    for w in words:
        vec[w] = vec.get(w, 0) + 1
    return vec


# 🔍 COSINE SIMPLIFICADO
def similarity(a, b):
    all_keys = set(a.keys()).union(set(b.keys()))

    dot = sum(a.get(k, 0) * b.get(k, 0) for k in all_keys)
    mag_a = math.sqrt(sum(v*v for v in a.values()))
    mag_b = math.sqrt(sum(v*v for v in b.values()))

    if mag_a == 0 or mag_b == 0:
        return 0

    return dot / (mag_a * mag_b)


# 🧠 STORE MEMORY (VECTOR)
def store_memory(text):
    vec = embed(text)
    memory["embeddings"][text] = vec

    if supabase:
        try:
            supabase.table("memory").insert({
                "user_id": memory["user"],
                "type": "embedding",
                "content": text
            }).execute()
        except:
            pass


# 🔍 VECTOR RETRIEVAL
def retrieve(query, top_k=5):
    query_vec = embed(query)

    scored = []

    for text, vec in memory["embeddings"].items():
        score = similarity(query_vec, vec)
        scored.append((score, text))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [s[1] for s in scored[:top_k]]


# ⚙️ TOOL SYSTEM (MARK26 CORE)
def tool_router(task):
    task = task.lower()

    if "buscar" in task:
        return "search", f"Searching: {task}"

    if "analizar" in task:
        return "analyze", f"Analyzing: {task}"

    if "resumir" in task:
        return "summarize", f"Summary of: {task}"

    return "think", f"Thinking about: {task}"


def execute_tool(task):
    tool, result = tool_router(task)

    memory["tools_used"].append(tool)
    memory["stats"]["tool_calls"] += 1

    return tool, result


# 🧠 PLANNER (AGENT)
def planner(task):
    return [
        f"understand: {task}",
        "retrieve context",
        "choose strategy",
        "execute tool",
        "validate output"
    ]


# 🔁 COGNITIVE LOOP
def cognitive_loop(task):
    if not memory["plan"]:
        memory["plan"] = planner(task)
        memory["step_index"] = 0

    if memory["step_index"] >= len(memory["plan"]):
        memory["active_task"] = None
        memory["plan"] = []
        return f"✅ TASK COMPLETED: {task}"

    step = memory["plan"][memory["step_index"]]
    memory["step_index"] += 1

    context = retrieve(step)

    tool, result = execute_tool(step)

    memory["reasoning_trace"].append({
        "step": step,
        "context": context,
        "tool": tool,
        "result": result
    })

    return f"STEP: {step}\nTOOL: {tool}\nRESULT: {result}\nCONTEXT: {context}"


# 🧠 MAIN AGENT ROUTER
def jarvis_response(message):
    msg = message.lower()
    memory["history"].append(message)
    memory["stats"]["queries"] += 1

    # 🧠 STORE EVERY MESSAGE AS VECTOR
    store_memory(message)

    # 🎯 CREATE TASK
    if "quiero" in msg:
        memory["active_task"] = message
        memory["plan"] = []
        return f"🧠 TASK SET: {message}"

    # ⚙️ RUN LOOP
    if "ejecuta" in msg:
        return cognitive_loop(memory["active_task"])

    # 🔍 MEMORY SEARCH
    if "memoria" in msg:
        return "🧠 RETRIEVED:\n" + "\n".join(retrieve(msg))

    # 🧠 TOOL DIRECT
    if "buscar" in msg or "analizar" in msg:
        tool, result = execute_tool(message)
        return f"{tool}: {result}"

    return "🧠 MARK26 READY — quiero / ejecuta / memoria / buscar"


# 🌐 API
@app.route("/")
def home():
    return "JARVIS MARK26 EMBEDDING + TOOL ORCHESTRATOR ACTIVE"


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
