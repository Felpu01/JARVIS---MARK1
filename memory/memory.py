import time
from memory.storage import load_state, save_state
from memory.intelligence import classify_message, should_store

state = load_state()


def save_memory(key, value):

    if not should_store(str(value)):
        return

    category = classify_message(str(value))

    entry = {
        "value": value,
        "category": category,
        "timestamp": time.time()
    }

    state.setdefault(key, []).append(entry)

    save_state(key, state[key])

    state["last_active"] = time.time()
    save_state("last_active", state["last_active"])


def get_memory():
    return state
