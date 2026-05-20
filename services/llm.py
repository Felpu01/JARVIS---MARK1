import random


def ask_llm(message, context=""):

    responses = [
        f"Entendido. Procesando: {message}",
        f"He analizado tu mensaje: {message}",
        f"JARVIS Core operativo. Respuesta generada para: {message}",
        f"Sistemas activos. Detecté que dijiste: {message}",
        f"Procesamiento completo. Entrada recibida: {message}"
    ]

    return random.choice(responses)
