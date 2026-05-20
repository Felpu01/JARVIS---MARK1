from flask import Flask, request, jsonify
import os
import json

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

        # 🧠 CORE STATE
        "history": [],
        "goals": [],

        # 🧠 PLAN STATE
        "plan": [],
        "step_index": 0,

        # 🧠 EXECUTION STATE
        "last_step": None,
        "last_result": None,
        "failures": 0,

        # 📊 STATS
        "stats": {
            "messages": 0,
            "plans_created": 0,
            "replans": 0
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

    if any(x in msg for x in ["hola", "buenas"]):
        return "greeting"

    if any(x in msg for x in ["status", "estado"]):
        return "status"

    if any(x in msg for x in ["quiero", "meta", "objetivo"]):
        return "goal"

    if any(x in msg for x in ["continúa", "siguiente", "seguir", "avanza"]):
        return "continue"

    return "general"


# 🧠 GOAL ENGINE
def generate_goal(message):
    msg = message.lower()

    if "automatizar" in msg:
        return "Construir sistema automatizado funcional"

    if "bot" in msg:
        return "Crear bot inteligente modular"

    if "dinero" in msg:
        return "Optimizar sistema de generación de valor"

    return message


# 🧠 PLAN BUILDER
def build_plan(goal):
    return [
        f"Analizar objetivo: {goal}",
        "Definir arquitectura",
        "Diseñar módulos",
        "Implementar lógica base",
        "Integrar sistema",
        "Probar funcionamiento",
        "Optimizar resultados"
    ]


# 🧠 EXECUTOR
def execute_step(step):
    # simulación de ejecución
    if "error" in step.lower():
        return "FAIL"

    return f"OK: {step}"


# 🧠 SELF CHECK
def evaluate_step(result):
    return result != "FAIL"


# 🧠 REPLANNER (NUEVO MARK19 CORE)
def replan(goal, failed_step):
    memory["stats"]["replans"] += 1

    return [
        f"Re-analizar: {goal}",
        f"Corregir error en: {failed_step}",
        "Simplificar enfoque",
        "Reintentar ejecución",
        "Validar resultados"
    ]


# 🧠 NEXT STEP ENGINE
def next_step():
    if memory["step_index"] >= len(memory["plan"]):
        return None

    step = memory["plan"][memory["step_index"]]
    memory["step_index"] += 1

    return step


# 🧠 AGENT CORE MARK19
def jarvis_response(message):
    msg = message.lower()
    memory["stats"]["messages"] += 1

    intent = detect_intent(message)

    # 🎯 GOAL CREATION
    if intent == "goal":
        goal = generate_goal(message)
        memory["goals"].append(goal)

        plan = build_plan(goal)

        memory["plan"] = plan
        memory["step_index"] = 0
        memory["failures"] = 0

        memory["stats"]["plans_created"] += 1

        return (
            "🧠 GOAL REGISTERED\n"
            f"Goal: {goal}\n\n"
            "PLAN:\n" +
            "\n".join(f"{i+1}. {p}" for i, p in enumerate(plan))
        )

    # ▶️ EXECUTION LOOP
    if intent == "continue":
        step = next_step()

        if not step:
            return "🧠 PLAN COMPLETED SUCCESSFULLY"

        result = execute_step(step)
        memory["last_step"] = step
        memory["last_result"] = result

        # ❌ FAILURE DETECTED
        if not evaluate_step(result):
            memory["failures"] += 1

            if memory["failures"] >= 2:
                new_plan = replan(memory["goals"][-1], step)

                memory["plan"] = new_plan
                memory["step_index"] = 0
                memory["failures"] = 0

                return (
                    "⚠️ REPLANNING ACTIVATED\n"
                    + "\n".join(f"{i+1}. {p}" for i, p in enumerate(new_plan))
                )

            return f"⚠️ STEP FAILED: {step}"

        return (
            "🧠 EXECUTING\n"
            f"Step: {step}\n"
            f"Result: {result}\n"
            f"Progress: {memory['step_index']}/{len(memory['plan'])}\n"
            f"Failures: {memory['failures']}"
        )

    # 📊 STATUS
    if intent == "status":
        return (
            "🧠 MARK19 STATUS\n"
            f"Goals: {len(memory['goals'])}\n"
            f"Plan steps: {len(memory['plan'])}\n"
            f"Index: {memory['step_index']}\n"
            f"Failures: {memory['failures']}"
        )

    # 👋 GREETING
    if intent == "greeting":
        return "🧠 MARK19 AUTONOMOUS AGENT ONLINE"

    # 🧠 DEFAULT
    return (
        "🧠 IDLE AGENT\n"
        "Commands:\n"
        "- 'quiero automatizar X'\n"
        "- 'continúa'"
    )


# 🌐 ROUTES
@app.route("/")
def home():
    return "JARVIS MARK19 AUTONOMOUS REPLANNER ACTIVE"


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


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
