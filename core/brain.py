from memory.memory import save_memory
from memory.intelligence import classify_message
from core.decision_engine import decide, execute_decision

def brain(message):

    # 1. guardar memoria base
    save_memory("history", message)

    # 2. clasificar intención
    category = classify_message(message)

    # 3. decidir qué hacer
    decision = decide(message, category)

    # 4. ejecutar acción
    result = execute_decision(decision, message)

    return result
