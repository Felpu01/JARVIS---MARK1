import time
import json
from memory.storage import load_state, save_state

state = load_state()

def save_memory(key, value):

    if key == "history":
        state.setdefault("history", []).append(value)

    state["last_active"] = time.time()

    save_state(state)

def get_memory():
    return state
