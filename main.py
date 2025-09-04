import os
from flask import Flask, render_template, request, jsonify
import stripe

app = Flask(__name__)

# Claves de Stripe desde variables de entorno
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
stripe.api_key = STRIPE_SECRET_KEY

# Código secreto
ACCESS_CODE = os.environ.get("MAYROGA_ACCESS_CODE")

# Servicios disponibles
SERVICES = [
    {"id": 1, "name": "Sesión Risoterapia 30min", "price": 2000},
    {"id": 2, "name": "Sesión Personalizada 1hr", "price": 3500},
    {"id": 3, "name": "Paquete Corporativo", "price": 5000},
]

@app.route("/")
def index():
    return render_template("index.html", stripe_key=STRIPE_PUBLISHABLE_KEY, services=SERVICES)

@app.route("/access", methods=["POST"])
def access():
    code = request.json.get("code")
    if code == ACCESS_CODE:
        return jsonify({"access_granted": True})
    return jsonify({"access_granted": False}), 403

@app.route("/create-payment-intent", methods=["POST"])
def create_payment():
    service_id = int(request.json.get("service_id"))
    service = next((s for s in SERVICES if s["id"] == service_id), None)
    if not service:
        return jsonify({"error": "Servicio no encontrado"}), 404
    try:
        intent = stripe.PaymentIntent.create(
            amount=service["price"],
            currency="usd",
            metadata={"service_id": service_id, "service_name": service["name"]},
        )
        return jsonify({"client_secret": intent.client_secret})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
