import os
import requests


TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")


def ask_llm(message, context=""):

    try:

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/Llama-3-8b-chat-hf",
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
                ],
                "temperature": 0.7,
                "max_tokens": 300
            },
            timeout=60
        )

        data = response.json()

        print("TOGETHER RESPONSE:", data)

        if "error" in data:
            return f"LLM API Error: {data['error']}"

        if "choices" not in data:
            return f"LLM Invalid Response: {data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"LLM Exception: {str(e)}"
