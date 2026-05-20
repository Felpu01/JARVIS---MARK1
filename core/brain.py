from memory.memory import save_memory, get_memory
from memory.intelligence import (
    classify_message,
    summarize_history
)

from services.llm import ask_llm


def brain(message):

    # guardar mensaje
    save_memory("history", message)

    # cargar memoria
    memory = get_memory()

    history = memory.get("history", [])

    recent_history = []

    for item in history[-10:]:

        if isinstance(item, dict):
            recent_history.append(
                str(item.get("value", ""))
            )

    # resumir contexto
    context = summarize_history(
        recent_history
    )

    # clasificar
    category = classify_message(message)

    # IA REAL
    ai_response = ask_llm(
        message,
        context=str(context)
    )

    # guardar respuesta
    save_memory(
        "jarvis_responses",
        ai_response
    )

    return {
        "response": ai_response,
        "category": category,
        "memory_size": len(history)
    }
