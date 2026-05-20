from flask import Flask, request, jsonify
import os
import json
import time

app = Flask(__name__)

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
        "goals": [],
        "plans": {},

        # 🧠 EXECUTION STATE
        "current_step": {},
        "failures": {},

        # 🧠 AGENT STATE
        "last_thought": None,
        "last_run": 0,

        # ⚙️ SCHEDULER
        "interval_seconds": 10,

        # 📊 STATS
        "stats": {
            "messages": 0,
            "auto_runs": 0,
            "plans": 0
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
        return "goal"

    if any(x in msg for x in ["ejecuta", "run", "continúa", "siguiente"]):
        return "run"

    if any(x in msg for x in ["status", "estado"]):
        return "status"

    return "general"


# 🧠 TOOL SYSTEM (MARK21 CORE)
def tool_executor(tool, data):
    if tool == "log":
        return f"LOGGED: {data}"

    if tool == "analyze":
        return f"ANALYZED: {data}"

    if tool == "simulate":
        return f"SIMULATION RESULT: {data}"

    return "UNKNOWN TOOL"


# 🧠 GOAL SYSTEM
def create_goal(message):
    return message


def build_plan(goal):
    return [
        f"Analizar objetivo: {goal}",
        "Dividir en subproblemas",
        "Construir arquitectura",
        "Implementar base",
        "Integrar sistema",
        "Testear",
        "Optimizar"
    ]


def next_step(goal):
    plan = memory["plans"].get(goal, [])
    index = memory["current_step"].get(goal, 0)

    if index >= len(plan):
        return None

    step = plan[index]
    memory["current_step"][goal] = index + 1

    return step


# 🧠 AUTONOMOUS ENGINE (MARK21 CORE)
def autonomous_tick():
    memory["stats"]["auto_runs"] += 1
    now = time.time()

    # ⏱️ throttle (evita spam en render)
    if now - memory["last_run"] < memory["interval_seconds"]:
        return

    memory["last_run"] = now

    if not memory["goals"]:
        memory["last_thought"] = "idle - no goals"
        return

    goal = memory["goals"][0]

    if goal not in memory["plans"]:
        memory["plans"][goal] = build_plan(goal)
        memory["current_step"][goal] = 0
        memory["failures"][goal] = 0
        memory["stats"]["plans"] += 1

        memory["last_thought"] = f"Plan created: {goal}"
        return

    step = next_step(goal)

    if step is None:
        memory["last_thought"] = f"Goal completed: {goal}"
        memory["goals"].pop(0)
        return

    # 🧠 TOOL USAGE DECISION
    if "analizar" in step.lower():
        result = tool_executor("analyze", step)

    elif "testear" in step.lower():
        result = tool_executor("simulate", step)

    else:
        result = tool_executor("log", step)

    memory["last_thought"] = f"{step} -> {result}"


# 🧠 ENGINE RESPONSE
def jarvis_response(message):
    memory["stats"]["messages"] += 1

    intent = detect_intent(message)

    if intent == "goal":
        goal = create_goal(message)
        memory["goals"].append(goal)

        return (
            "🧠 GOAL REGISTERED\n"
            f"{goal}\n"
            "Agent will process automatically"
        )

    if intent == "run":
        autonomous_tick()
        return f"🧠 MANUAL TICK\n{memory['last_thought']}"

    if intent == "status":
        return (
            "🧠 MARK21 STATUS\n"
            f"Goals: {len(memory['goals'])}\n"
            f"Plans: {len(memory['plans'])}\n"
            f"Last: {memory['last_thought']}\n"
            f"Auto interval: {memory['interval_seconds']}s"
        )

    return (
        "🧠 MARK21 AUTONOMOUS AGENT\n"
        "Commands:\n"
        "- quiero automatizar X\n"
        "- status\n"
        "- ejecuta"
    )


# 🌐 AUTO HEARTBEAT ENDPOINT (CLAVE MARK21)
@app.route("/tick", methods=["GET"])
def tick():
    autonomous_tick()
    save_memory()

    return jsonify({
        "status": "tick executed",
        "last_thought": memory["last_thought"],
        "goals": memory["goals"]
    })


# 💬 CHAT
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "empty message"}), 400

    memory["history"].append(message)

    response = jarvis_response(message)

    save_memory()

    return jsonify({
        "response": response,
        "memory": memory
    })


# 🌐 HOME
@app.route("/")
def home():
    return "JARVIS MARK21 AUTONOMOUS SCHEDULER ACTIVE"


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
