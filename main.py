import os
from flask import Flask, request, jsonify
import stripe

app = Flask(__name__)

# 🔑 Clave secreta de Stripe (debes configurarla en Render como variable de entorno STRIPE_SECRET_KEY)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

@app.route("/")
def home():
    return "Servidor de May Roga funcionando ✅"

# Crear sesión de pago real con Stripe Checkout
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json()
    service = data.get("service")
    price = data.get("price")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": service},
                    "unit_amount": int(price * 100),  # Stripe trabaja en centavos
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://asistente-virtual-may-roga.onrender.com/success",
            cancel_url="https://asistente-virtual-may-roga.onrender.com/cancel",
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Validar código secreto
@app.route("/validate-access-code", methods=["POST"])
def validate_access_code():
    data = request.get_json()
    code = data.get("access_code")

    if code == os.environ.get("MAYROGA_ACCESS_CODE"):  
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route("/success")
def success():
    return "✅ Pago realizado con éxito. Gracias por usar May Roga."

@app.route("/cancel")
def cancel():
    return "❌ Pago cancelado. Intenta de nuevo."
