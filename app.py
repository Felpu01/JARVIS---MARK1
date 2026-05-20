from flask import Flask
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
    return {
        "status": "online",
        "ai": "JARVIS Core V1",
        "state": "running"
    }


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
