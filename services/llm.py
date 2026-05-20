import random


def ask_llm(message, context=""):

    message = message.lower()

    # respuestas contextuales básicas

    if "hola" in message:
        return "Hola. JARVIS Core online y operativo."

    if "como estas" in message:
        return "Todos los sistemas funcionando correctamente."

    if "quien soy" in message:
        return (
            "Eres el usuario principal de este sistema JARVIS."
        )

    if "memoria" in message:
        return (
            f"Tengo acceso a contexto reciente: {context}"
        )

    # respuestas dinámicas

    responses = [

        f"Procesado correctamente: {message}",

        f"He registrado tu mensaje: {message}",

        f"Contexto actualizado correctamente.",

        f"Análisis completado sobre: {message}",

        f"Patrones conversacionales detectados."
    ]

    return random.choice(responses)
