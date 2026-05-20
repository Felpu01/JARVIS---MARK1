import time
from memory.storage import load_state, save_state
from memory.intelligence import classify_message, should_store

state = load_state()

def save_memory(key, value):

    if not should_store(str(value)):
        return

    category = classify_message(str(value))

    state.setdefault(key, []).append({
        "value": value,
        "category": category,
        "timestamp": time.time()
    })

    save_state(key, {
        "value": value,
        "category": category
    })

    state["last_active"] = time.time()

def get_memory():
    return state
