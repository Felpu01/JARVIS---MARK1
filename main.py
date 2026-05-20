from flask import Flask, request, jsonify

app = Flask(__name__)

# 🧠 MEMORIA MARK4 (incluye perfil inteligente)
memory = {
    "user": "Matias",
    "last_message": None,
    "last_response": None,

    "history": [],
    "commands": [],
    "questions": [],
    "profile": {}
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

# 🧠 MOTOR JARVIS
def jarvis_response(message):
    message_lower = message.lower()

    intent = detect_intent(message)

    last = memory.get("last_message")
    history = memory.get("history", [])

    context_hint = ""
    if len(history) > 1:
        context_hint = f"(Contexto: antes dijiste '{history[-2]}')"

    # 🔥 RESPUESTAS POR INTENCIÓN
    if intent == "greeting":
        return "Afirmativo. JARVIS en línea. ¿Cómo puedo asistirte?"

    elif intent == "status":
        return "Todos los sistemas operativos. Sin anomalías detectadas."

    elif intent == "question":
        return f"Procesando consulta: '{message}'. Sistema analizando respuesta."

    elif intent == "command":
        return f"Comando recibido: '{message}'. Ejecutando lógica de sistema."

    # 🧠 RESPUESTAS ESPECÍFICAS
    if "quién eres" in message_lower:
        return "Soy JARVIS MARK4, evolución de tu asistente inteligente."

    elif "hora" in message_lower:
        return "Aún no tengo acceso al reloj del sistema, pero será integrado en próximas versiones."

    elif "ayuda" in message_lower:
        return "Puedes decir: hola, estado, quién eres, hora o cualquier instrucción."

    elif "qué dije" in message_lower or "antes" in message_lower:
        if last:
            return f"Tu último mensaje fue: '{last}'. {context_hint}"
        else:
            return "No tengo suficiente historial aún."

    # 🧠 fallback inteligente
    else:
        return f"Afirmativo. He procesado: '{message}'. {context_hint} Sistema operativo activo."

# 🌐 endpoint principal
@app.route("/")
def home():
    return "JARVIS Core MARK4 activo"

# 💬 chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    # 🧠 guardar memoria estructurada
    memory["history"].append(message)
    memory["last_message"] = message

    # 🧠 guardar comandos / preguntas
    if "recordá" in message.lower() or "recuerda" in message.lower():
        memory["commands"].append(message)

    elif any(x in message.lower() for x in ["qué", "cómo", "por qué"]):
        memory["questions"].append(message)

    # 🧠 🆕 PERFIL INTELIGENTE (MARK4 PASO 1)
    msg = message.lower()

    if "me gusta" in msg or "me interesa" in msg:
        memory["profile"]["interest"] = message

    if "soy" in msg:
        memory["profile"]["identity"] = message

    if "quiero" in msg:
        memory["profile"]["intent"] = message

    # 🧠 respuesta
    response = jarvis_response(message)

    memory["last_response"] = response

    return jsonify({
        "response": response,
        "memory": memory,
        "profile": memory["profile"]
    })

# 🚀 RUN (Render compatible)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
