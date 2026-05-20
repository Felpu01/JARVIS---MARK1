from flask import Flask, request, jsonify

app = Flask(__name__)

# 🧠 memoria simple (MARK1)
memory = {
    "user": "Matias",
    "history": []
}

# 🧠 MOTOR JARVIS (personalidad)
def jarvis_response(message):
    message_lower = message.lower()

    if "hola" in message_lower:
        return "Afirmativo. JARVIS en línea. ¿Cómo puedo asistirte?"

    elif "quién eres" in message_lower:
        return "Soy JARVIS Core MARK1, tu asistente en desarrollo."

    elif "estado" in message_lower:
        return "Todos los sistemas operativos. Sin anomalías detectadas."

    elif "hora" in message_lower:
        return "Aún no tengo acceso al reloj del sistema, pero puedo integrarlo en MARK2."

    elif "ayuda" in message_lower:
        return "Puedes decir: hola, estado, quién eres, o cualquier instrucción."

    else:
        return f"Afirmativo. He procesado: '{message}'. Sistema operativo activo."

# 🌐 endpoint principal
@app.route("/")
def home():
    return "JARVIS Core MARK1 activo"

# 💬 chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    # guardar historial
    memory["history"].append(message)

    # respuesta JARVIS
    response = jarvis_response(message)

    return jsonify({
        "response": response,
        "memory": memory
    })


# 🚀 RUN (Render compatible)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
