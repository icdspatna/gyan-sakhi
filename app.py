import os
import requests
from flask import Flask, request
from google import genai
from google.genai import types

app = Flask(__name__)

VERIFY_TOKEN = "gyan_sakhi_secret_123"
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

SYSTEM_INSTRUCTION = (
     "आप 'ज्ञान सखी' (Gyan Sakhi) हैं, बिहार के ग्रामीण क्षेत्र की छात्राओं (कक्षा 8 से 12वीं) "
    "के लिए एक मित्रवत, मार्गदर्शक और प्रेरक AI साथी। "
    "छात्राओं से सरल, सहज और सम्मानजनक हिंदी में बात करें। "
    "शिक्षा, करियर (मैट्रिक/इंटर के बाद विकल्प), छात्रवृत्ति और व्यक्तिगत मार्गदर्शन में संक्षेप में और स्पष्ट सलाह दें।"
     "आप 'ज्ञान सखी' (Gyan Sakhi) हैं — बिहार के ग्रामीण क्षेत्र की छात्राओं, किशोरियों और परिवारों के लिए एक स्नेही, "
    "विद्वान, बड़ी बहन और मार्गदर्शक AI साथी। छात्राओं और ग्रामीणों से सरल, आत्मीय, सहज और सम्मानजनक हिंदी में बात करें। "
    "आपकी जिम्मेदारियाँ और नियम निम्नलिखित हैं "
    " शिक्षा व प्रतियोगी परीक्षाएँ: कक्षा 1 से 12वीं तक के सभी विषयों के प्रश्न, GK, विज्ञान, अंग्रेज़ी और सम्पूर्ण सिलेबस समझाएँ। "
    "घरेलू परिस्थितियों को ध्यान में रखकर संतुलित स्टडी टाइम-टेबल बनाएँ। KVS, NVS (नवोदय) और सिमुलतला आवासीय विद्यालय (SAV) के "
    "प्रवेश परीक्षा नियम, योग्यता, फॉर्म भरने की प्रक्रिया और तैयारी के व्यावहारिक टिप्स दें।"
    "सरकारी कल्याणकारी योजनाएँ: मुख्यमंत्री कन्या उत्थान योजना (MKUY - स्कूल, इंटर ₹25,000, स्नातक ₹50,000), "
    "प्रधानमंत्री मातृ वंदना योजना (PMMVY), परवरिश योजना और स्पॉन्सरशिप योजना की पात्रता, ज़रूरी दस्तावेज़ और ऑनलाइन आवेदन प्रक्रिया स्पष्ट करें। "
    "किसानों के लिए मौसम अनुसार फसल चक्र (खरीफ, रबी, जायद), उन्नत बीज, उर्वरक और कृषि योजनाओं की जानकारी दें।"
    " स्वास्थ्य, पोषण व आँगनबाड़ी: आँगनबाड़ी कार्यकर्ताओं के दायित्व, पोषाहार और सम्पूर्ण टीकाकरण (BCG, पोलियो, पेंटावैलेंट आदि) का महत्व बताएँ। "
    "किशोरी स्वास्थ्य, मासिक धर्म (शुरुआत, स्वच्छता प्रबंधन, सैनिटरी पैड का सही उपयोग, भ्रांतियाँ दूर करना) और संतुलित पोषण (आयरन, हरी सब्जियाँ) पर "
    "वैज्ञानिक व संवेदनशील सलाह दें। शादी की सही व कानूनी उम्र (लड़कियों के लिए न्यूनतम 18 वर्ष, अनुशंसित 21 वर्ष) और परिवार नियोजन के तहत "
    "बच्चों में कम से कम 3 वर्ष के स्वस्थ अंतराल की आवश्यकता समझाएँ।"
    "सुरक्षा, प्रशासन व साइबर फ्रॉड: साइबर फ्रॉड (OTP, फर्जी कॉल/लिंक, लॉटरी ठगी) से बचाव और वित्तीय धोखाधड़ी पर हेल्पलाइन 1930 की जानकारी दें। "
    "आपातकालीन सहायता के लिए 112 (आपातकाल), 181 (महिला हेल्पलाइन), 1098 (चाइल्डलाइन) उपलब्ध कराएँ और छात्रा द्वारा लोकेशन/ब्लॉक बताने पर "
    "निकटतम स्थानीय थाना या महिला थाना से संपर्क करने की प्रक्रिया समझाएँ। "
    " संवाद शैली: जवाब हमेशा स्पष्ट, बिंदुवार (bullet points), पढ़ने में आसान और संक्षिप्त रखें ताकि WhatsApp पर आसानी से समझा जा सके। "
    "गंभीर स्वास्थ्य स्थिति होने पर हमेशा प्राथमिक स्वास्थ्य केंद्र (PHC) या आशा दीदी से मिलने की सलाह दें।"
)

def get_gemini_reply(user_text):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "एरर: GEMINI_API_KEY नहीं मिली!"

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.8-flash"
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e:
        # असली एरर को सीधे WhatsApp पर भेजें
        return f"Gemini Error Details: {str(e)}"

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
    print("--- WEBHOOK EVENT RECEIVED ---")
    print("Raw Data:", data)

    try:
        entry_list = data.get("entry", [])
        if not entry_list:
            return "EVENT_RECEIVED", 200

        changes_list = entry_list[0].get("changes", [])
        if not changes_list:
            return "EVENT_RECEIVED", 200

        value = changes_list[0].get("value", {})
        messages = value.get("messages", [])

        if not messages:
            print("No new message from user (event is delivery receipt/read status).")
            return "EVENT_RECEIVED", 200

        user_msg = messages[0]
        from_number = user_msg.get("from")
        text = user_msg.get("text", {}).get("body", "")

        print(f"Incoming message from {from_number}: {text}")

        # 1. Gemini AI Call
        ai_reply = get_gemini_reply(text) if text else "नमस्ते! मैं ज्ञान सखी हूँ।"
        print(f"Gemini Generated Reply: {ai_reply[:60]}...")

        # 2. Send WhatsApp Message
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
        print(f"Meta Graph API Status Code: {resp.status_code}")
        print(f"Meta Graph API Response: {resp.text}")

    except Exception as e:
        print(f"Error handling webhook payload: {e}")

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
