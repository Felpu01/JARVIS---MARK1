import os
import requests


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def ask_llm(message, context=""):

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://jarvis-mark1.onrender.com",
                "X-Title": "JARVIS Core",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are JARVIS Core, an advanced AI assistant. "
                            "Be intelligent, calm, concise and helpful."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"""
Context:
{context}

User:
{message}
"""
                    }
                ]
            },
            timeout=60
        )

        data = response.json()

        print("OPENROUTER RESPONSE:", data)

        if "error" in data:
            return f"LLM API Error: {data['error']}"

        if "choices" not in data:
            return f"LLM Invalid Response: {data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"LLM Exception: {str(e)}"
