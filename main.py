from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# 📦 ARCHIVO DE MEMORIA PERSISTENTE
MEMORY_FILE = "memory.json"


# 🧠 CARGAR MEMORIA DESDE DISCO
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {
        "user": "Matias",
        "history": [],
        "commands": [],
        "questions": [],
        "profile": {
            "role": None,
            "interests": [],
            "goals": []
        }
    }


# 💾 GUARDAR MEMORIA EN DISCO
def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


memory = load_memory()


# 🧠 INTENCIÓN
def detect_intent(message):
    msg = message.lower()

    if any(x in msg for x in ["hola", "buenas", "hey"]):
        return "greeting"

    if any(x in msg for x in ["quién", "qué es", "explica", "cómo", "por qué"]):
        return "question"

    if any(x in msg for x in ["recordá", "recuerda", "guarda"]):
        return "command"

    if any(x in msg for x in ["estado", "status"]):
        return "status"

    return "general"


# 🧠 ACTUALIZAR PERFIL CON PESO
def update_profile(message):
    msg = message.lower()

    if "soy" in msg:
        memory["profile"]["role"] = message

    if "me gusta" in msg or "me interesa" in msg:
        memory["profile"]["interests"].append(message)

    if "quiero" in msg:
        memory["profile"]["goals"].append(message)


# 🧠 MOTOR JARVIS MARK7
def jarvis_response(message):
    msg = message.lower()

    intent = detect_intent(message)

    history = memory["history"]
    profile = memory["profile"]

    context = f"(Antes dijiste '{history[-2]}')" if len(history) > 1 else ""

    # 🔥 RESPUESTAS BASE
    if intent == "greeting":
        return "Afirmativo. JARVIS en línea. ¿Cómo puedo asistirte?"

    if intent == "status":
        return "Todos los sistemas operativos. Sin anomalías detectadas."

    if intent == "question":
        return f"Analizando consulta: '{message}'. Procesamiento activo."

    if intent == "command":
        return f"Comando registrado: '{message}'. Ejecutando sistema."

    # 🧠 MEMORIA REAL (PERSISTENTE)
    role = profile.get("role")
    interests = profile.get("interests", [])
    goals = profile.get("goals", [])

    if role or interests or goals:
        return (
            f"🧠 MODO JARVIS ACTIVO\n"
            f"Rol: {role}\n"
            f"Intereses: {interests}\n"
            f"Objetivos: {goals}\n\n"
            f"Procesado: '{message}' {context}"
        )

    return f"Afirmativo. He procesado: '{message}' {context}"


# 🌐 HOME
@app.route("/")
def home():
    return "JARVIS Core MARK7 activo"


# 💬 CHAT
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    # 🧠 memoria base
    memory["history"].append(message)

    if "recordá" in message.lower():
        memory["commands"].append(message)

    if any(x in message.lower() for x in ["qué", "cómo", "por qué"]):
        memory["questions"].append(message)

    # 🧠 perfil
    update_profile(message)

    # 🧠 respuesta
    response = jarvis_response(message)
    memory["last_response"] = response

    # 💾 persistencia REAL
    save_memory()

    return jsonify({
        "response": response,
        "memory": memory
    })


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
