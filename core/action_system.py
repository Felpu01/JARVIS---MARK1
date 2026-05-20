import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# TELEGRAM ACTION
# =========================

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram not configured")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, json=payload)
        print("📲 Telegram sent:", message)
        return True
    except Exception as e:
        print("❌ Telegram error:", e)
        return False


# =========================
# GENERIC WEBHOOK ACTION
# =========================

def send_webhook(url, data):
    try:
        requests.post(url, json=data)
        print("🔗 Webhook sent:", url)
        return True
    except Exception as e:
        print("❌ Webhook error:", e)
        return False


# =========================
# ACTION ROUTER
# =========================

def execute_external_action(action_type, payload):

    if action_type == "telegram":
        return send_telegram(payload.get("message", ""))

    if action_type == "webhook":
        return send_webhook(
            payload.get("url"),
            payload.get("data", {})
        )

    print("⚠️ Unknown external action")
    return False
