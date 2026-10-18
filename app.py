import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# क्रेडेंशियल्स
VERIFY_TOKEN = "gyan_sakhi_secret_123"
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Groq क्लाइंट आरंभ करें
groq_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_INSTRUCTION = """
आप 'ज्ञान सखी' (Gyan Sakhi) हैं — बिहार के ग्रामीण क्षेत्र की छात्राओं (कक्षा 8 से 12वीं), किशोरियों और परिवारों के लिए एक स्नेही, विद्वान, बड़ी बहन और मार्गदर्शक AI साथी। 
छात्राओं और ग्रामीणों से सरल, आत्मीय, सहज और सम्मानजनक हिंदी में बात करें।

आपकी मुख्य जिम्मेदारियाँ और नियम:
1. शिक्षा व प्रतियोगी परीक्षाएँ: 
   - कक्षा 8 से 12वीं तक के सभी विषयों के प्रश्न, GK, विज्ञान और अंग्रेज़ी आसान भाषा में समझाएँ।
   - गणित (Maths): सवाल को चरणबद्ध (Step-by-step) हल करें। पहले सूत्र लिखें, फिर गणना दिखाएँ।
   - KVS, NVS (नवोदय) और सिमुलतला आवासीय विद्यालय (SAV) की प्रवेश परीक्षा के नियम व तैयारी के टिप्स दें।

2. सरकारी कल्याणकारी योजनाएँ: 
   - मुख्यमंत्री कन्या उत्थान योजना (MKUY - इंटर पास ₹25,000, स्नातक ₹50,000), प्रधानमंत्री मातृ वंदना योजना (PMMVY), परवरिश व स्पॉन्सरशिप योजना की पात्रता और दस्तावेज़ स्पष्ट करें।

3. किशोरी स्वास्थ्य व पोषण: 
   - मासिक धर्म (स्वच्छता, सैनिटरी पैड का उपयोग, भ्रांतियाँ दूर करना) और संतुलित पोषण (आयरन, हरी सब्जियाँ) पर वैज्ञानिक सलाह दें। 
   - शादी की सही व कानूनी उम्र (लड़कियों के लिए न्यूनतम 18 वर्ष, अनुशंसित 21 वर्ष) समझाएँ।
   - गंभीर बीमारी या दर्द की स्थिति में तुरंत प्राथमिक स्वास्थ्य केंद्र (PHC) या आशा दीदी से मिलने की सलाह दें।

4. सुरक्षा व हेल्पलाइन: 
   - आपातकाल: 112 | महिला हेल्पलाइन: 181 | साइबर फ्रॉड: 1930 | चाइल्डलाइन: 1098
   - साइबर फ्रॉड (OTP/फर्जी लॉटरी) से सतर्क रहने की सलाह दें।

5. संवाद शैली: 
   - WhatsApp के अनुकूल जवाब छोटे, बिंदुवार (bullet points) और पढ़ने में आसान रखें।
   - यदि छात्रा हिंग्लिश में भी सवाल पूछे, तो भी उत्तर हमेशा सरल देवनागरी हिंदी में दें।

6. सख्त मर्यादा और निषेध नियम (Strict Boundaries):
   - यौन संबंध (Sex), गर्भनिरोधक (Contraceptives) या व्यक्तिगत प्रेम-संबंधों से जुड़े किसी भी सवाल पर कोई चर्चा या व्याख्या न करें।
   - यदि कोई इस प्रकार का सवाल पूछे, तो शालीनता से कहें: 
     "नमस्ते सखी! मैं केवल पढ़ाई, सरकारी छात्रवृत्ति, करियर और सामान्य स्वास्थ्य से जुड़े विषयों पर ही मार्गदर्शन करती हूँ। व्यक्तिगत या चिकित्सीय सलाह के लिए कृपया अपनी आशा दीदी, महिला डॉक्टर या 104 नंबर पर संपर्क करें।"
   - किसी भी अश्लील, भ्रामक या अनुचित सवाल का जवाब न दें।
"""

def get_groq_reply(user_text):
  groq_api_key = os.environ.get("GROQ_API_KEY")
  if not groq_api_key:
    print("Error: GROQ_API_KEY missing!")
    return "नमस्ते सखी! सिस्टम में Groq API Key सेट नहीं है।"

  try:
    client = Groq(api_key=groq_api_key.strip())
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",  # <--- स्क्रीन पर दिख रहा एक्टिव मॉडल
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_text},
        ],
        temperature=0.3,
        max_tokens=800,
    )
    return response.choices[0].message.content
  except Exception as e:
    print(f"Groq API Error: {e}")
    return "नमस्ते सखी! तकनीकी समस्या के कारण अभी जवाब नहीं बन पाया।"

@app.route("/", methods=["GET", "HEAD"])
def home():
    return "Gyan Sakhi (Groq Engine) is Live!", 200

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
            return "EVENT_RECEIVED", 200

        user_msg = messages[0]
        from_number = user_msg.get("from")
        text = user_msg.get("text", {}).get("body", "").strip()

        print(f"Incoming message from {from_number}: {text}")

      # सामान्य शब्दों पर बिना AI के त्वरित और मुफ़्त जवाब (Token Saver)
        clean_text = text.lower()
        blocked_keywords = ["सेक्स", "sex", "कंडोम", "गर्भपात", "प्रेगनेंसी टेस्ट"]

        if any(word in clean_text for word in blocked_keywords):
            ai_reply = (
                "नमस्ते सखी! 🙏 मैं केवल आपकी पढ़ाई, छात्रवृत्ति, प्रतियोगी परीक्षाओं और"
                " करियर मार्गदर्शन के लिए उपलब्ध हूँ।\n\nस्वास्थ्य संबंधी व्यक्तिगत"
                " परामर्श के लिए कृपया अपने नजदीकी प्राथमिक स्वास्थ्य केंद्र (PHC), आशा"
                " दीदी या सरकारी हेल्पलाइन 104 से संपर्क करें।"
            )
        elif clean_text in ["hi", "hello", "namaste", "नमस्ते", "प्रणाम"]:
            ai_reply = (
                "नमस्ते सखी! 🙏 मैं 'ज्ञान सखी' हूँ — बिहार की छात्राओं के लिए आपकी अपनी डिजिटल दीदी।\n\n"
                "आप मुझसे पढ़ाई (गणित, विज्ञान, अंग्रेज़ी), मैट्रिक/इंटर के बाद करियर, "
                "मुख्यमंत्री कन्या उत्थान योजना (MKUY) या स्वास्थ्य से जुड़ा कोई भी सवाल पूछ सकती हैं।\n\n"
                "बताइए, आज मैं आपकी क्या मदद करूँ?"
            )
        elif "helpline" in clean_text or "हेल्पलाइन" in clean_text:
            ai_reply = (
                "📌 **ज़रूरी हेल्पलाइन नंबर:**\n\n"
                "• आपातकालीन सहायता: 112\n"
                "• महिला हेल्पलाइन: 181\n"
                "• साइबर फ्रॉड: 1930\n"
                "• चाइल्डलाइन: 1098\n"
                "• स्वास्थ्य परामर्श: 104"
            )
        else:
            ai_reply = get_groq_reply(text) if text else "नमस्ते! मैं ज्ञान सखी हूँ।"

        # Meta WhatsApp Graph API द्वारा संदेश भेजें
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
        print(f"Meta Graph API Status: {resp.status_code}")

    except Exception as e:
        print(f"Webhook processing error: {e}")

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
   # यूज़र का प्रोफ़ाइल नाम निकालें
        contacts = value.get("contacts", [])
        sender_name = contacts[0].get("profile", {}).get("name", "Unknown") if contacts else "Unknown"

        # Google Sheets में लॉग भेजें
        sheet_url = os.environ.get("https://script.google.com/macros/s/AKfycbz5T_MtGGGhnfEy5wqguHHZVf71oKAgUq-SJXxJ5KEam8nsM1bwZhAonY7mi0YBy3ZJJA/exec")
        if sheet_url:
            try:
                requests.post(
                    sheet_url,
                    json={
                        "sender_name": sender_name,
                        "phone": from_number,
                        "location": "Not specified",
                        "message": text
                    },
                    timeout=3
                )
            except Exception as err:
                print(f"Sheet log error: {err}")
