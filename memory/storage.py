import json
import os


MEMORY_FILE = "memory_data.json"


# =========================
# LOAD ALL MEMORY
# =========================
def load_state():

    if not os.path.exists(MEMORY_FILE):

        return {
            "history": [],
            "tasks": [],
            "last_active": 0
        }

    try:

        with open(MEMORY_FILE, "r") as f:

            state = json.load(f)

            return state

    except Exception as e:

        print("⚠️ Local memory load error:", e)

        return {
            "history": [],
            "tasks": [],
            "last_active": 0
        }


# =========================
# SAVE SINGLE EVENT
# =========================
def save_state(key, value):

    try:

        state = load_state()

        if key not in state:
            state[key] = []

        # si es lista → append
        if isinstance(state[key], list):

            state[key].append(value)

        else:

            state[key] = value

        with open(MEMORY_FILE, "w") as f:

            json.dump(state, f, indent=2)

    except Exception as e:

        print("⚠️ Local memory save error:", e)
