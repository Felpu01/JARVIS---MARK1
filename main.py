from flask import Flask, request, jsonify

app = Flask(__name__)

# 🧠 MEMORIA MARK6 (estructurada real)
memory = {
    "user": "Matias",
    "last_message": None,
    "last_response": None,
    "history": [],
    "commands": [],
    "questions": [],
    "profile": {
        "role": None,
        "interests": [],
        "goals": []
    }
}

# 🧠 DETECTOR DE INTENCIÓN
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


# 🧠 ACTUALIZADOR DE PERFIL LIMPIO (MARK6)
def update_profile(message):
    msg = message.lower()

    # 👤 role
    if "soy" in msg:
        memory["profile"]["role"] = message

    # 💡 interests
    if "me gusta" in msg or "me interesa" in msg:
        memory["profile"]["interests"].append(message)

    # 🎯 goals
    if "quiero" in msg:
        memory["profile"]["goals"].append(message)


# 🧠 MOTOR JARVIS (MARK6)
def jarvis_response(message):
    msg = message.lower()

    intent = detect_intent(message)

    last = memory["last_message"]
    history = memory["history"]

    context = f"(Contexto: antes dijiste '{history[-2]}')" if len(history) > 1 else ""

    profile = memory["profile"]

    # 🔥 INTENTOS BASE
    if intent == "greeting":
        return "Afirmativo. JARVIS en línea. ¿Cómo puedo asistirte?"

    if intent == "status":
        return "Todos los sistemas operativos. Sin anomalías detectadas."

    if intent == "question":
        return f"Analizando consulta: '{message}'. Procesamiento activo."

    if intent == "command":
        return f"Comando registrado: '{message}'. Ejecutando lógica."

    # 🧠 RESPUESTAS CONTEXTUALES INTELIGENTES
    role = profile.get("role")
    interests = profile.get("interests", [])
    goals = profile.get("goals", [])

    if role or interests or goals:
        return (
            f"Modo JARVIS activo.\n"
            f"Rol detectado: {role}\n"
            f"Intereses: {interests}\n"
            f"Objetivos: {goals}\n\n"
            f"Procesado: '{message}' {context}"
        )

    return f"Afirmativo. He procesado: '{message}' {context}"


# 🌐 HOME
@app.route("/")
def home():
    return "JARVIS Core MARK6 activo"


# 💬 CHAT
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    # 🧠 memoria base
    memory["history"].append(message)
    memory["last_message"] = message

    # 🧠 intención tracking
    if "recordá" in message.lower():
        memory["commands"].append(message)

    if any(x in message.lower() for x in ["qué", "cómo", "por qué"]):
        memory["questions"].append(message)

    # 🧠 actualizar perfil limpio
    update_profile(message)

    # 🧠 respuesta
    response = jarvis_response(message)
    memory["last_response"] = response

    return jsonify({
        "response": response,
        "memory": memory
    })


# 🚀 RUN
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
