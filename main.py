import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe

# --- Configuración ---
app = Flask(__name__)
CORS(app)  # Permite peticiones desde cualquier origen
PORT = int(os.environ.get("PORT", 10000))

# --- Claves desde Render ---
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
ACCESS_CODE = os.environ.get("MAYROGA_ACCESS_CODE")
stripe.api_key = STRIPE_SECRET_KEY

# --- Rutas ---
@app.route('/')
def home():
    return jsonify({"message": "Asistente Virtual May Roga backend funcionando"}), 200

@app.route('/validate-access-code', methods=['POST'])
def validate_access_code():
    data = request.get_json()
    code = data.get('access_code', '')
    if code == ACCESS_CODE:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 200

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.get_json()
    service_name = data.get('service', 'Servicio')
    price = data.get('price', 1)  # precio en USD

    try:
        # Stripe espera precio en centavos
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': service_name,
                    },
                    'unit_amount': int(float(price) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"https://asistente-virtual-may-roga.onrender.com/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"https://asistente-virtual-may-roga.onrender.com/cancel",
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/success')
def payment_success():
    return jsonify({"message": "Pago realizado correctamente. ¡Gracias!"}), 200

@app.route('/cancel')
def payment_cancel():
    return jsonify({"message": "Pago cancelado."}), 200

# --- Ejecutar app ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
