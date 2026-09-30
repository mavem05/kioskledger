import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_whatsapp_receipt(to_number: str, text: str):
    """
    Sends a text message back to the merchant via the Meta Cloud API.
    """
    token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_ID")
    
    # Meta's API endpoint for sending messages
    url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"📨 Reply Status: {response.status_code}")
    except Exception as e:
        print(f"Failed to send reply: {e}")