import os
import requests

token = os.getenv("TELEGRAM_BOT_TOKEN")
url = "https://telegram-bot-production-9d73f095.up.railway.app/webhook"

response = requests.post(f"https://api.telegram.org/bot{token}/setWebhook", data={"url": url})
print(response.json())
