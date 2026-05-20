from memory.memory import save_memory

def handle_task(message):
    save_memory("tasks", message)
    return "Tarea guardada."
