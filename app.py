import os
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
VERIFY_TOKEN = "gyansakhi123"

client = genai.Client(api_key=GEMINI_API_KEY)

@app.route("/", methods=["GET"])
def home():
    return "Gyan Sakhi Bot is Active!", 200

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification token mismatch", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data.get("entry"):
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])

                if messages:
                    msg = messages[0]
                    from_number = msg.get("from")

                    if msg.get("type") == "text":
                        user_text = msg["text"]["body"]

                        prompt = f"""तुम 'ज्ञान सखी' हो — बिहार की ग्रामीण छात्राओं (8वीं-12वीं) के लिए एक दयालु और समझदार AI दीदी।
छात्रा ने पूछा है: "{user_text}"
अगर सवाल भोजपुरी, मगही या हिंदी में हो, उसे समझो और 2-3 वाक्यों में बहुत ही सरल, शुद्ध और आत्मीय हिंदी में उत्तर दो।"""

                        try:
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=prompt
                            )
                            reply_text = response.text
                        except Exception:
                            reply_text = "माफ़ करना सखी, उत्तर खोजने में थोड़ी समस्या हुई। दोबारा पूछो ना!"

                        send_whatsapp_message(from_number, reply_text)

    return jsonify({"status": "success"}), 200

def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
