from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe
import os

app = Flask(__name__)
CORS(app)

# --- Configuración de Stripe ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")  # En Render, en Environment

# --- Código secreto que los clientes deben ingresar ---
ACCESS_CODE = os.environ.get("ACCESS_CODE", "1234")  # Cambia esto en Render

@app.route("/validate-access-code", methods=["POST"])
def validate_access_code():
    data = request.get_json()
    code = data.get("access_code", "")
    if code == ACCESS_CODE:
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json()
    service_name = data.get("service")
    price = data.get("price")

    try:
        # Stripe usa centavos, multiplicamos por 100
        amount = int(float(price) * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": service_name},
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=os.environ.get("SUCCESS_URL", "https://asistente-virtual-may-roga.onrender.com/success"),
            cancel_url=os.environ.get("CANCEL_URL", "https://asistente-virtual-may-roga.onrender.com/cancel"),
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --- Ruta de prueba ---
@app.route("/")
def index():
    return "Asistente Virtual May Roga Backend funcionando ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
