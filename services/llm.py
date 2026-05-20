import os
import requests


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def ask_llm(message, context=""):

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are JARVIS Core, an advanced AI assistant. "
                            "Be intelligent, concise, calm and helpful."
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

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"LLM Error: {str(e)}"
