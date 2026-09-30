import httpx

TOKEN = "8841275189:AAGtBUCeYAnyX2jXHzALjoCvb74Yabw_cSM"
NGROK_URL = "https://persuaded-appliance-gladiator.ngrok-free.dev"

url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={NGROK_URL}/webhook"

print("Sending webhook command to Telegram...")
# Added a 60-second timeout to prevent the connection drop
try:
    response = httpx.get(url, timeout=60.0)
    print("Telegram Response:", response.json())
except Exception as e:
    print("Connection still failing:", e)