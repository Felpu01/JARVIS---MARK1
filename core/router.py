from modules.tasks import handle_task
from modules.status import handle_status
from modules.alerts import handle_alert

def route_intent(message):

    msg = message.lower()

    # TASKS
    if "recordá" in msg:
        return handle_task(message)

    # STATUS
    if "estado" in msg:
        return handle_status()

    # ALERTS / EVENTS
    if "revisar" in msg:
        return handle_alert(message)

    return f"Procesado: {message}"
