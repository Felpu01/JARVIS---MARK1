from flask import Flask, request, jsonify

app = Flask(__name__)

# 🧠 MEMORIA MARK2
memory = {
    "user": "Matias",
    "last_message": None,
    "last_response": None,
    "history": []
}

# 🧠 MOTOR JARVIS (con contexto)
def jarvis_response(message):
    message_lower = message.lower()

    last = memory.get("last_message")
    history = memory.get("history", [])

    # contexto simple
    context_hint = ""
    if len(history) > 1:
        context_hint = f"(Contexto: antes dijiste '{history[-2]}')"

    if "hola" in message_lower:
        return "Afirmativo. JARVIS en línea. ¿Cómo puedo asistirte?"

    elif "quién eres" in message_lower:
        return "Soy JARVIS MARK2, una evolución de tu asistente inteligente."

    elif "estado" in message_lower:
        return "Todos los sistemas operativos. Sin anomalías detectadas."

    elif "hora" in message_lower:
        return "Aún no tengo acceso al reloj del sistema, pero será integrado en MARK3."

    elif "ayuda" in message_lower:
        return "Puedes decir: hola, estado, quién eres, hora o preguntar lo que quieras."

    elif "qué dije" in message_lower or "antes" in message_lower:
        if last:
            return f"Tu último mensaje fue: '{last}'. {context_hint}"
        else:
            return "No tengo suficiente historial aún."

    else:
        return f"Afirmativo. He procesado: '{message}'. {context_hint} Sistema operativo activo."

# 🌐 endpoint principal
@app.route("/")
def home():
    return "JARVIS Core MARK2 activo"

# 💬 chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    # guardar memoria
    memory["history"].append(message)
    memory["last_message"] = message

    # respuesta
    response = jarvis_response(message)

    # guardar respuesta
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
