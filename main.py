from flask import Flask, request, jsonify
import os
import json
import time

app = Flask(__name__)

# 📦 MEMORY FILE
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
        "active_goal_index": 0,

        # 🧠 PLANS (MULTI GOAL)
        "plans": {},

        # 🧠 EXECUTION STATE
        "current_step": {},
        "failures": {},

        # 🧠 AGENT STATE
        "mode": "idle",
        "last_thought": None,

        # 📊 METRICS
        "stats": {
            "messages": 0,
            "loops": 0,
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

    if any(x in msg for x in ["hola", "hey"]):
        return "greeting"

    if "quiero" in msg:
        return "goal"

    if any(x in msg for x in ["ejecuta", "continúa", "siguiente"]):
        return "run"

    if any(x in msg for x in ["status", "estado"]):
        return "status"

    return "general"


# 🧠 GOAL CREATION
def create_goal(message):
    return message


# 🧠 PLAN GENERATOR
def generate_plan(goal):
    return [
        f"Analizar: {goal}",
        "Definir estructura",
        "Construir lógica base",
        "Integrar componentes",
        "Testear sistema",
        "Optimizar resultado"
    ]


# 🧠 EXECUTOR
def execute(step):
    if "error" in step.lower():
        return False, "FAIL"

    return True, f"OK: {step}"


# 🧠 NEXT STEP
def get_next_step(goal):
    plan = memory["plans"].get(goal, [])
    index = memory["current_step"].get(goal, 0)

    if index >= len(plan):
        return None

    step = plan[index]
    memory["current_step"][goal] = index + 1

    return step


# 🧠 THINKING ENGINE (NUEVO MARK20 CORE)
def agent_think():
    memory["stats"]["loops"] += 1

    if not memory["goals"]:
        memory["last_thought"] = "No goals active"
        return

    goal = memory["goals"][memory["active_goal_index"]]

    if goal not in memory["plans"]:
        plan = generate_plan(goal)
        memory["plans"][goal] = plan
        memory["current_step"][goal] = 0
        memory["failures"][goal] = 0
        memory["stats"]["plans"] += 1

        memory["last_thought"] = f"Plan created for {goal}"
        return

    step = get_next_step(goal)

    if step is None:
        memory["last_thought"] = f"Goal completed: {goal}"
        memory["active_goal_index"] = (memory["active_goal_index"] + 1) % len(memory["goals"])
        return

    success, result = execute(step)

    if not success:
        memory["failures"][goal] += 1

        if memory["failures"][goal] >= 2:
            memory["plans"][goal] = generate_plan(goal)
            memory["current_step"][goal] = 0
            memory["failures"][goal] = 0

            memory["last_thought"] = f"Replanning triggered for {goal}"
            return

    memory["last_thought"] = f"Executed: {step} -> {result}"


# 🧠 MAIN ENGINE (MARK20)
def jarvis_response(message):
    memory["stats"]["messages"] += 1

    intent = detect_intent(message)

    # 🎯 GOAL MODE
    if intent == "goal":
        goal = create_goal(message)
        memory["goals"].append(goal)

        plan = generate_plan(goal)
        memory["plans"][goal] = plan
        memory["current_step"][goal] = 0
        memory["failures"][goal] = 0

        return (
            "🧠 GOAL REGISTERED\n"
            f"{goal}\n\n"
            "PLAN:\n" +
            "\n".join(f"{i+1}. {p}" for i, p in enumerate(plan))
        )

    # ▶️ RUN MANUAL STEP
    if intent == "run":
        agent_think()

        return f"🧠 AGENT STEP EXECUTED\n{memory['last_thought']}"

    # 📊 STATUS
    if intent == "status":
        return (
            "🧠 MARK20 STATUS\n"
            f"Goals: {len(memory['goals'])}\n"
            f"Plans: {len(memory['plans'])}\n"
            f"Last thought: {memory['last_thought']}\n"
            f"Mode: {memory['mode']}"
        )

    # 👋 DEFAULT
    return (
        "🧠 MARK20 AGENT READY\n"
        "Commands:\n"
        "- quiero automatizar X\n"
        "- ejecuta\n"
        "- status"
    )


# 🌐 LOOP ENDPOINT (NUEVO)
@app.route("/loop", methods=["POST"])
def loop():
    agent_think()
    save_memory()

    return jsonify({
        "status": "loop executed",
        "memory": memory
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
    return "JARVIS MARK20 CONTINUOUS AGENT ACTIVE"


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
