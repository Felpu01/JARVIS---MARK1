import time
from memory.memory import get_memory
from memory.intelligence import detect_user_pattern
from modules.alerts import push_event

def autonomy_loop():

    while True:
        mem = get_memory()

        history = mem.get("history", [])

        patterns = detect_user_pattern(history)

        # 🔥 detección de comportamiento
        if patterns.get("task_user", 0) > 3:
            push_event("Usuario con alta carga de tareas", "medium")

        if patterns.get("status_checker", 0) > 2:
            push_event("Usuario monitorea estado frecuentemente", "low")

        time.sleep(15)
