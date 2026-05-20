from flask import Flask, render_template, request, jsonify
import threading
import os

from api.routes import api
from core.autonomy import autonomy_loop

app = Flask(__name__)

app.register_blueprint(api)


# =========================
# HOME ROUTE
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# CHAT ROUTE (si no lo tenés en api)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    # 🔥 placeholder (tu IA real puede estar en api.routes)
    return jsonify({
        "response": f"Recibido: {message}"
    })


# =========================
# AUDIO ROUTE (🔥 FIX CLAVE)
# =========================
@app.route("/audio", methods=["POST"])
def audio():

    if "audio" not in request.files:
        return jsonify({"response": "No audio recibido"})

    audio_file = request.files["audio"]

    path = "audio.webm"
    audio_file.save(path)

    # =========================
    # 🔥 TRANSCRIPCIÓN (WHISPER)
    # =========================
    try:
        import whisper

        model = whisper.load_model("base")
        result = model.transcribe(path, language="es")

        text = result["text"]

    except Exception as e:
        print("WHISPER ERROR:", e)
        text = "No se pudo transcribir audio"

    return jsonify({
        "response": text
    })


# =========================
# START APP
# =========================
if __name__ == "__main__":

    # loop autónomo en background
    threading.Thread(
        target=autonomy_loop,
        daemon=True
    ).start()

    # puerto dinámico Render
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
