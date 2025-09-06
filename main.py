import os
import json
import stripe
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from openai import OpenAI

# -------------------------
# Configuración inicial
# -------------------------
app = Flask(__name__)
CORS(app)

# Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
URL_SITE = os.getenv("URL_SITE")

# Código secreto
SECRET_CODE = os.getenv("MAYROGA_ACCESS_CODE")

# Firebase
firebase_config = json.loads(os.getenv("__firebase_config__"))
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# OpenAI fallback
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# Rutas principales
# -------------------------
@app.route("/")
def index():
    return render_template("index.html", stripe_key=PUBLISHABLE_KEY, url_site=URL_SITE)

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

# -------------------------
# Crear sesión de pago Stripe
# -------------------------
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json()
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": data["product"]},
                    "unit_amount": int(float(data["amount"]) * 100),  # en centavos
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{URL_SITE}/success",
            cancel_url=f"{URL_SITE}/cancel",
        )
        return jsonify({"id": session.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# Chat con IA y código secreto
# -------------------------
@app.route("/assistant-stream", methods=["GET", "POST"])
def assistant_stream():
    try:
        if request.method == "POST":
            data = request.get_json()
        else:
            data = request.args

        secret = data.get("secret", "")

        # ✅ Validar código secreto
        if secret != SECRET_CODE:
            return jsonify({"error":"Código incorrecto"}), 401

        user_message = data.get("message", "")
        service = data.get("service", "general")

        # Guardar en Firebase
        db.collection("chats").add({
            "user_message": user_message,
            "service": service,
            "secret": secret
        })

        # 1️⃣ Intentar con Gemini
        try:
            response = gemini_model.generate_content(user_message)
            respuesta = response.text
        except Exception:
            # 2️⃣ Fallback a OpenAI
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres Asistente May Roga, experto en risoterapia y bienestar natural."},
                    {"role": "user", "content": user_message},
                ],
            )
            respuesta = completion.choices[0].message.content

        return jsonify({"reply": respuesta})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# Webhook Stripe
# -------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRECT")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return "Firma inválida", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("✅ Pago exitoso:", session.get("id"))

    return "ok", 200

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
