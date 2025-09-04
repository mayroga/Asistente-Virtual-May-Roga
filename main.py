import os
from flask import Flask, render_template, request, jsonify
import stripe

app = Flask(__name__)

# Claves de Stripe desde variables de entorno
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')

# Código secreto desde variable de entorno
ACCESS_CODE = os.environ.get('MAYROGA_ACCESS_CODE')

# Página principal
@app.route("/")
def index():
    return render_template("index.html", stripe_key=STRIPE_PUBLISHABLE_KEY)

# Validar código secreto
@app.route("/validate_code", methods=["POST"])
def validate_code():
    data = request.get_json()
    code = data.get("code", "")
    if code == ACCESS_CODE:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

# Crear sesión de pago Stripe
@app.route("/create_checkout_session", methods=["POST"])
def create_checkout_session():
    data = request.get_json()
    service_name = data.get("service")
    price = data.get("price")
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": service_name},
                    "unit_amount": int(float(price) * 100),  # convertir a centavos
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{os.environ.get('RENDER_EXTERNAL_URL', 'https://asistente-virtual-may-roga.onrender.com')}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.environ.get('RENDER_EXTERNAL_URL', 'https://asistente-virtual-may-roga.onrender.com')}/cancel",
        )
        return jsonify({"id": session.id})
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/success")
def success():
    return "<h1>Pago completado correctamente. ¡Gracias!</h1>"

@app.route("/cancel")
def cancel():
    return "<h1>Pago cancelado. Intenta nuevamente.</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
