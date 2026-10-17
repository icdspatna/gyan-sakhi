import os
import requests
from flask import Flask, request
from google import genai

app = Flask(__name__)

VERIFY_TOKEN = "gyan_sakhi_secret_123"
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SYSTEM_INSTRUCTION = (
    "आप 'ज्ञान सखी' (Gyan Sakhi) हैं, बिहार के ग्रामीण क्षेत्र की छात्राओं (कक्षा 8 से 12वीं) "
    "के लिए एक मित्रवत, मार्गदर्शक और प्रेरक AI साथी। "
    "छात्राओं से सरल, सहज और सम्मानजनक हिंदी में बात करें। "
    "शिक्षा, करियर (मैट्रिक/इंटर के बाद विकल्प), छात्रवृत्ति और व्यक्तिगत मार्गदर्शन में संक्षेप में और स्पष्ट सलाह दें।"
)

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

@app.route("/", methods=["GET", "HEAD"])
def home():
    return "Gyan Sakhi Bot is Live!", 200

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return challenge, 200
    return "Verification token mismatch", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("--- NEW WEBHOOK EVENT ---")
    print("Payload:", data)

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            print("Status update received, no user message.")
            return "EVENT_RECEIVED", 200

        user_msg = messages[0]
        from_number = user_msg.get("from")
        text = user_msg.get("text", {}).get("body", "")

        print(f"User Message from {from_number}: {text}")

        # Gemini AI Call
        ai_reply = "नमस्ते! मैं ज्ञान सखी हूँ।"
        if client and text:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{SYSTEM_INSTRUCTION}\n\nछात्रा का सवाल: {text}"
                )
                ai_reply = response.text
                print(f"Gemini Replied: {ai_reply[:50]}...")
            except Exception as e:
                print(f"Gemini API Error: {e}")
                ai_reply = "सखी, मुझे आपका संदेश मिला। मैं अभी सोचने में व्यस्त हूँ, कृपया थोड़ी देर बाद पुनः प्रयास करें।"

        # Send WhatsApp Message
        send_url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": from_number,
            "type": "text",
            "text": {"body": ai_reply}
        }

        resp = requests.post(send_url, json=payload, headers=headers)
        print(f"WhatsApp API Status: {resp.status_code}")
        print(f"WhatsApp API Response: {resp.text}")

    except Exception as e:
        print(f"Processing Error: {e}")

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
