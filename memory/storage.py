import json
import os

FILE = "runtime/state.json"

def load_state():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)

    return {
        "history": [],
        "tasks": [],
        "last_active": 0
    }

def save_state(state):
    with open(FILE, "w") as f:
        json.dump(state, f)
