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
# CHAT SIMPLE (ESTABLE)
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    message = data.get("message", "")

    # respuesta simple estable
    return jsonify({
        "response": f"Recibido: {message}"
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
