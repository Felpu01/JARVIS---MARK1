import time
from memory.memory import get_memory
from modules.alerts import push_event

def autonomy_loop():

    while True:
        mem = get_memory()

        last_active = mem.get("last_active", time.time())

        # si inactivo
        if time.time() - last_active > 60:

            tasks = mem.get("tasks", [])

            if tasks:
                push_event(f"Tarea pendiente: {tasks[0]}", "medium")

        time.sleep(10)
