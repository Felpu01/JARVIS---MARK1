from flask import Flask, request, jsonify

app = Flask(__name__)

# 🧠 MEMORIA MARK5
memory = {
    "user": "Matias",
    "last_message": None,
    "last_response": None,

    "history": [],
    "commands": [],
    "questions": [],
    "profile": {}
}

# 🧠 DETECTOR DE INTENCIÓN
def detect_intent(message):
    msg = message.lower()

    if any(x in msg for x in ["hola", "buenas", "hey"]):
        return "greeting"

    if any(x in msg for x in ["quién", "qué es", "explica", "cómo", "por qué"]):
        return "question"

    if any(x in msg for x in ["recordá", "recuerda", "guarda"]):
        return "command"

    if any(x in msg for x in ["estado", "status"]):
        return "status"

    return "general"

# 🧠 MOTOR JARVIS (PERSONALIZADO + PESOS)
def jarvis_response(message):
    message_lower = message.lower()

    intent = detect_intent(message)

    last = memory.get("last_message")
    history = memory.get("history", [])

    context_hint = ""
    if len(history) > 1:
        context_hint = f"(Contexto: antes dijiste '{history[-2]}')"

    # 🔥 RESPUESTAS POR INTENCIÓN
    if intent == "greeting":
        return "Afirmativo. JARVIS en línea. ¿Cómo puedo asistirte?"

    elif intent == "status":
        return "Todos los sistemas operativos. Sin anomalías detectadas."

    elif intent == "question":
        return f"Procesando consulta: '{message}'. Sistema analizando respuesta."

    elif intent == "command":
        return f"Comando recibido: '{message}'. Ejecutando lógica de sistema."

    # 🧠 RESPUESTAS ESPECÍFICAS
    if "quién eres" in message_lower:
        return "Soy JARVIS MARK5, evolución de tu asistente inteligente."

    elif "hora" in message_lower:
        return "Aún no tengo acceso al reloj del sistema, pero será integrado en próximas versiones."

    elif "ayuda" in message_lower:
        return "Puedes decir: hola, estado, quién eres, hora o cualquier instrucción."

    elif "qué dije" in message_lower or "antes" in message_lower:
        if last:
            return f"Tu último mensaje fue: '{last}'. {context_hint}"
        else:
            return "No tengo suficiente historial aún."

    # 🧠 PERSONALIZACIÓN CON PESO (MARK5 PASO 2)
    profile = memory.get("profile", {})

    def get_value(key):
        if key in profile:
            return profile[key].get("value", "")
        return ""

    def get_weight(key):
        if key in profile:
            return profile[key].get("weight", 0)
        return 0

    identity = get_value("identity")
    interest = get_value("interest")
    intent_profile = get_value("intent")

    identity_w = get_weight("identity")
    interest_w = get_weight("interest")

    # 🧠 DECISIÓN BASADA EN PESO
    if interest_w >= identity_w and interest_w > 0:
        return f"Afirmativo Matias. Detecto fuerte interés en '{interest}'. Priorizaré este tema en futuras respuestas. He procesado: '{message}'."

    elif identity_w > interest_w and identity_w > 0:
        return f"Afirmativo Matias. Tu perfil como '{identity}' es dominante. Ajustando respuestas a ese contexto. He procesado: '{message}'."

    elif identity or interest:
        return f"Afirmativo Matias. Perfil detectado ({identity}, {interest}). He procesado: '{message}'."

    # 🧠 fallback
    return f"Afirmativo. He procesado: '{message}'. {context_hint} Sistema operativo activo."

# 🔧 FUNCIÓN MARK5: MEMORIA CON PESO
def update_profile(key, value):
    if "profile" not in memory:
        memory["profile"] = {}

    if key not in memory["profile"]:
        memory["profile"][key] = {
            "value": value,
            "weight": 1
        }
    else:
        memory["profile"][key]["weight"] += 1
        memory["profile"][key]["value"] = value

# 🌐 endpoint principal
@app.route("/")
def home():
    return "JARVIS Core MARK5 activo"

# 💬 chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    # 🧠 guardar memoria
    memory["history"].append(message)
    memory["last_message"] = message

    # 🧠 comandos / preguntas
    if "recordá" in message.lower() or "recuerda" in message.lower():
        memory["commands"].append(message)

    elif any(x in message.lower() for x in ["qué", "cómo", "por qué"]):
        memory["questions"].append(message)

    # 🧠 perfil básico
    msg = message.lower()

    if "me gusta" in msg or "me interesa" in msg:
        update_profile("interest", message)

    if "soy" in msg:
        update_profile("identity", message)

    if "quiero" in msg:
        update_profile("intent", message)

    # 🧠 respuesta
    response = jarvis_response(message)

    memory["last_response"] = response

    return jsonify({
        "response": response,
        "memory": memory,
        "profile": memory["profile"]
    })

# 🚀 RUN (Render compatible)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
