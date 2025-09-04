import os
from flask import Flask, render_template, request, jsonify
import stripe

app = Flask(__name__)

# Claves de Stripe desde variables de entorno
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")

# Código secreto para acceso libre
ACCESS_CODE = os.environ.get("MAYROGA_ACCESS_CODE")

# Lista de servicios (puedes agregar o modificar)
SERVICES = [
    {"id": 1, "name": "Sesión de risoterapia 30 min", "price": 20},
    {"id": 2, "name": "Sesión de bienestar 45 min", "price": 30},
    {"id": 3, "name": "Paquete empresarial", "price": 50},
]

@app.route("/")
def index():
    return render_template(
        "index.html",
        stripe_key=STRIPE_PUBLISHABLE_KEY,
        services=SERVICES
    )

@app.route("/validate-code", methods=["POST"])
def validate_code():
    data = request.get_json()
    code = data.get("code", "")
    if code == ACCESS_CODE:
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json()
    service_id = int(data.get("service_id"))
    service = next((s for s in SERVICES if s["id"] == service_id), None)
    if not service:
        return jsonify({"error": "Servicio no encontrado"}), 400

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': service["name"]},
                'unit_amount': int(service["price"] * 100),  # en centavos
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.host_url + "?success=true",
        cancel_url=request.host_url + "?canceled=true",
    )
    return jsonify({"id": session.id})

if __name__ == "__main__":
    app.run(debug=True)
