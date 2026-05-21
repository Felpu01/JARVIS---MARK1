from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# =========================
# MEMORIA SIMPLE EN RAM
# =========================
memory = {}


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# CHAT CON MEMORIA
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    message = data.get("message", "").lower().strip()

    global memory

    # =========================
    # GUARDAR NOMBRE
    # =========================
    if "me llamo" in message:
        name = message.replace("me llamo", "").strip()
        memory["name"] = name
        reply = f"Ok, voy a recordarlo. Hola {name}."

    # =========================
    # CONSULTAR NOMBRE
    # =========================
    elif "como me llamo" in message or "quien soy" in message:
        name = memory.get("name")
        if name:
            reply = f"Te llamas {name}."
        else:
            reply = "Todavía no me dijiste tu nombre."

    # =========================
    # SALUDO
    # =========================
    elif "hola" in message:
        name = memory.get("name")
        if name:
            reply = f"Hola {name}, estoy operativo."
        else:
            reply = "Hola, estoy operativo."

    # =========================
    # DEFAULT
    # =========================
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
