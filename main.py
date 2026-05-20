from flask import Flask, request, jsonify

app = Flask(__name__)

# 🧠 MEMORIA MARK2 (mejorada)
memory = {
    "user": "Matias",
    "last_message": None,
    "last_response": None,
    "history": []
}

# 🧠 MOTOR JARVIS (personalidad)
def jarvis_response(message):
    message_lower = message.lower()

    if "hola" in message_lower:
        return "Afirmativo. JARVIS en línea. ¿Cómo puedo asistirte?"

    elif "quién eres" in message_lower:
        return "Soy JARVIS Core MARK1 evolucionando a MARK2, tu asistente en desarrollo."

    elif "estado" in message_lower:
        return "Todos los sistemas operativos. Sin anomalías detectadas."

    elif "hora" in message_lower:
        return "Aún no tengo acceso al reloj del sistema, pero será agregado en próximas versiones."

    elif "ayuda" in message_lower:
        return "Puedes decir: hola, estado, quién eres, hora o cualquier instrucción."

    else:
        return f"Afirmativo. He procesado: '{message}'. Sistema operativo activo."

# 🌐 endpoint principal
@app.route("/")
def home():
    return "JARVIS Core MARK2 activo"

# 💬 chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    # guardar historial
    memory["history"].append(message)
    memory["last_message"] = message

    # respuesta JARVIS
    response = jarvis_response(message)

    # guardar última respuesta
    memory["last_response"] = response

    return jsonify({
        "response": response,
        "memory": memory
    })

# 🚀 RUN (Render compatible)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
