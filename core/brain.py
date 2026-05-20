from core.router import route_intent
from memory.memory import save_memory, get_memory

def brain(message):

    save_memory("history", message)

    response = route_intent(message)

    return response
