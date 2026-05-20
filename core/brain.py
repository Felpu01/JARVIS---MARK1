from memory.memory import save_memory, get_memory
from memory.intelligence import (
    classify_message,
    summarize_history,
    detect_user_pattern
)

from core.decision_engine import (
    decide,
    execute_decision
)


# =========================
# JARVIS PERSONALITY
# =========================

PERSONALITY = """
You are JARVIS Core.

You are intelligent, calm, efficient and helpful.
You speak clearly and naturally.
You maintain conversational context.
You assist the user like an advanced AI system.
"""


# =========================
# MAIN BRAIN
# =========================

def brain(message):

    # =========================
    # SAVE USER MESSAGE
    # =========================

    save_memory("history", message)

    # =========================
    # LOAD MEMORY
    # =========================

    memory = get_memory()

    history = memory.get("history", [])

    recent_history = []

    for item in history[-10:]:

        if isinstance(item, dict):
            recent_history.append(
                str(item.get("value", ""))
            )

        else:
            recent_history.append(str(item))

    # =========================
    # CONTEXT ENGINE
    # =========================

    summarized_context = summarize_history(
        recent_history
    )

    user_patterns = detect_user_pattern(
        recent_history
    )

    # =========================
    # INTENT CLASSIFICATION
    # =========================

    category = classify_message(message)

    # =========================
    # DECISION ENGINE
    # =========================

    decision = decide(
        message,
        category
    )

    # =========================
    # ACTION EXECUTION
    # =========================

    result = execute_decision(
        decision,
        message
    )

    # =========================
    # SAVE RESPONSE
    # =========================

    save_memory("jarvis_responses", result)

    # =========================
    # RETURN FINAL RESPONSE
    # =========================

    return {
        "response": result,
        "category": category,
        "decision": decision,
        "patterns": user_patterns,
        "context_size": len(summarized_context)
    }
