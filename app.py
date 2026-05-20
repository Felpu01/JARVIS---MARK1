from flask import Flask
import threading

from api.routes import api
from core.autonomy import autonomy_loop

app = Flask(__name__)
app.register_blueprint(api)

if __name__ == "__main__":
    threading.Thread(target=autonomy_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=1000)
