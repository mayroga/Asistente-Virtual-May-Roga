from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe
import os

app = Flask(__name__)
CORS(app)  # Permite que el frontend en otro dominio pueda llamar al backend

# Claves de Stripe (secret key solo en backend)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
ACCESS_CODE = os.environ.get("MAYROGA_ACCESS_CODE")  # Código secreto de acceso

@app.route('/validate-access-code', methods=['POST'])
def validate_access_code():
    data = request.get_json()
    code = data.get("access_code")
    if code == ACCESS_CODE:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.get_json()
    service_name = data.get("service")
    price = int(float(data.get("price")) * 100)  # Stripe requiere precio en centavos
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": service_name},
                    "unit_amount": price,
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

if __name__ == '__main__':
    app.run(debug=True)
