import time
from memory.storage import load_state, save_state

state = load_state()

def save_memory(key, value):

    if key == "history":
        state.setdefault("history", []).append(value)
        save_state("history", value)

    elif key == "tasks":
        state.setdefault("tasks", []).append(value)
        save_state("tasks", value)

    state["last_active"] = time.time()
    save_state("last_active", state["last_active"])

def get_memory():
    return state
