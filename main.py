import os
from flask import Flask, request, jsonify
import openai
import stripe

# --- Configuración ---
app = Flask(__name__)

# OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # clave secreta
YOUR_DOMAIN = "https://asistente-virtual-may-roga.onrender.com"

# Código secreto
SECRET_CODE = "MAYROGA2025"

# Estado de servicios pagados
paid_services = set()

# --- Servicios disponibles ---
SERVICES = {
    "risoterapia": {"price": 800, "duration": "5:00 min"},
    "express": {"price": 300, "duration": "0:48 min"},
    "horoscopo": {"price": 600, "duration": "1:20 min"},
    # Aquí puedes añadir los demás servicios...
}

# --- Crear sesión de pago ---
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    service_id = data.get("service")

    if service_id not in SERVICES:
        return jsonify({"error": "Servicio no encontrado"}), 404

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": service_id},
                    "unit_amount": SERVICES[service_id]["price"],
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{YOUR_DOMAIN}/success.html?service={service_id}",
            cancel_url=f"{YOUR_DOMAIN}/cancel.html",
            metadata={"service": service_id}
        )
        return jsonify({"id": checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

# --- Webhook de Stripe ---
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        return str(e), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        service_id = session.get("metadata", {}).get("service")
        if service_id:
            paid_services.add(service_id)

    return "OK", 200

# --- Chat con control de acceso ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    service_id = data.get("service")
    user_code = data.get("secret_code", "")

    # Validar acceso: código secreto o pago
    if user_code == SECRET_CODE or service_id in paid_services:
        user_message = data.get("message", "")
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres el asistente de May Roga especializado en risoterapia y bienestar natural."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200
            )
            reply = response.choices[0].message.content
            return jsonify({"reply": reply})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Acceso denegado. Paga el servicio o usa el código secreto."}), 403

# --- Main ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
