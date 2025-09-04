import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe
import google.generativeai as genai

# =========================
# CONFIGURACIONES
# =========================
app = Flask(__name__)
CORS(app)

# Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Google Generative AI
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# RUTAS PRINCIPALES
# =========================

@app.route("/")
def home():
    return jsonify({"message": "🌿 Asistente Virtual May Roga activo"})

# Validación del código de acceso
@app.route("/validate-access-code", methods=["POST"])
def validate_access_code():
    data = request.json
    access_code = data.get("code")

    if access_code == os.environ.get("ACCESS_CODE"):
        return jsonify({"valid": True})
    return jsonify({"valid": False}), 401

# Crear sesión de pago con Stripe
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        data = request.json
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": data.get("product", "Servicio de bienestar")},
                    "unit_amount": int(data.get("amount", 1000)),  # en centavos
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=data.get("success_url", "https://tu-web.com/success"),
            cancel_url=data.get("cancel_url", "https://tu-web.com/cancel"),
        )
        return jsonify({"id": session.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Respuestas del asistente con Gemini
@app.route("/assistant", methods=["POST"])
def assistant():
    try:
        data = request.json
        user_message = data.get("message", "")

        response = model.generate_content(user_message)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# EJECUCIÓN LOCAL
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
