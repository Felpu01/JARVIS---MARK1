from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# CHAT (JARVIS BÁSICO REAL)
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    message = data.get("message", "").lower().strip()

    # =========================
    # LÓGICA SIMPLE TIPO ASISTENTE
    # =========================
    if "hola" in message:
        reply = "Hola, estoy operativo."

    elif "quien eres" in message or "quién eres" in message:
        reply = "Soy JARVIS Core, tu asistente personal."

    elif "que puedes hacer" in message or "qué puedes hacer" in message:
        reply = "Puedo responder mensajes y ejecutar comandos básicos."

    elif "como estas" in message or "cómo estás" in message:
        reply = "Estoy funcionando correctamente."

    elif "adios" in message or "chau" in message:
        reply = "Hasta luego."

    else:
        reply = "Entendido: " + message

    return jsonify({
        "response": reply
    })


# =========================
# START
# =========================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
