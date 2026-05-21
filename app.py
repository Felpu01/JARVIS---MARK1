from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

memory = {}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    message = data.get("message", "").lower().strip()

    global memory

    # =========================
    # GUARDAR NOMBRE (ROBUSTO)
    # =========================
    if "me llamo" in message:

        name = message.replace("me llamo", "").strip()

        if name:
            memory["name"] = name
            reply = f"Perfecto, voy a recordarlo. Hola {name}."
        else:
            reply = "Decime tu nombre después de 'me llamo'."

    # =========================
    # CONSULTA NOMBRE (ROBUSTO)
    # =========================
    elif "como me llamo" in message or "cómo me llamo" in message:

        name = memory.get("name")

        if name:
            reply = f"Te llamas {name}."
        else:
            reply = "Todavía no me dijiste tu nombre."

    # =========================
    # QUIÉN SOY
    # =========================
    elif "quien soy" in message or "quién soy" in message:

        name = memory.get("name")

        if name:
            reply = f"Eres {name}."
        else:
            reply = "No sé quién eres todavía."

    # =========================
    # SALUDO
    # =========================
    elif "hola" in message:

        name = memory.get("name")

        if name:
            reply = f"Hola {name}, estoy operativo."
        else:
            reply = "Hola, estoy operativo."

    else:
        reply = "Entendido: " + message


    return jsonify({
        "response": reply
    })


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
