from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# 📁 archivo de memoria persistente
MEMORY_FILE = "memory.json"

# 🧠 cargar memoria desde archivo
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {
        "user": "Matias",
        "last_message": None,
        "last_response": None,
        "history": []
    }

# 💾 guardar memoria en archivo
def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# 🧠 MEMORIA GLOBAL (persistente)
memory = load_memory()

# 🧠 MOTOR JARVIS (con contexto)
def jarvis_response(message):
    message_lower = message.lower()

    last = memory.get("last_message")
    history = memory.get("history", [])

    context_hint = ""
    if len(history) > 1:
        context_hint = f"(Contexto: antes dijiste '{history[-2]}')"

    if "hola" in message_lower:
        return "Afirmativo. JARVIS en línea. ¿Cómo puedo asistirte?"

    elif "quién eres" in message_lower:
        return "Soy JARVIS MARK3, evolución de tu asistente inteligente."

    elif "estado" in message_lower:
        return "Todos los sistemas operativos. Sin anomalías detectadas."

    elif "hora" in message_lower:
        return "Aún no tengo acceso al reloj del sistema, pero será mejorado en MARK3."

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
    return "JARVIS Core MARK3 activo"

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

    # 💾 persistencia real
    save_memory()

    return jsonify({
        "response": response,
        "memory": memory
    })

# 🚀 RUN (Render compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
