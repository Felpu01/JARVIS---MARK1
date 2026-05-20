from memory.memory import save_memory, get_memory
from memory.intelligence import (
    classify_message,
    summarize_history,
    detect_user_pattern
)

from services.llm import ask_llm


def brain(message):

    # guardar mensaje usuario
    save_memory("history", message)

    # cargar memoria global
    memory = get_memory()

    history = memory.get("history", [])

    recent_history = []

    # extraer últimos mensajes
    for item in history[-15:]:

        if isinstance(item, dict):

            value = item.get("value", "")

            recent_history.append(str(value))

    # resumen contextual
    context = summarize_history(
        recent_history
    )

    # detectar patrones
    patterns = detect_user_pattern(
        recent_history
    )

    # clasificar intención
    category = classify_message(message)

    # respuesta IA
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
        "memory_size": len(history),
        "patterns": patterns,
        "context_size": len(context)
    }
