from flask import Flask, request, jsonify

app = Flask(__name__)

# 🧠 memoria simple (V1)
memory = {
    "user": "Matias",
    "history": []
}

@app.route("/")
def home():
    return "JARVIS Core V1 activo"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    # guardar historial
    memory["history"].append(message)

    # respuesta simple tipo JARVIS
    response = f"Recibido: {message}. Sistema activo."

    return jsonify({
        "response": response,
        "memory": memory
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
