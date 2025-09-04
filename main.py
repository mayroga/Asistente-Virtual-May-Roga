from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe
import os

app = Flask(__name__)
CORS(app)  # Permite solicitudes desde cualquier origen, importante para tu frontend

# Stripe: usar la secret key configurada en Render como variable de entorno
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")  # NO poner aquí la key, se usa la de Render

# Código secreto de acceso (puedes cambiarlo después)
ACCESS_CODE = "12345"

# Endpoint para validar código secreto
@app.route("/validate-access-code", methods=["POST"])
def validate_access_code():
    data = request.get_json()
    if not data or "access_code" not in data:
        return jsonify({"success": False, "message": "Código no recibido"}), 400
    code = data["access_code"]
    if code == ACCESS_CODE:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

# Endpoint para crear sesión de Stripe Checkout
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json()
    if not data or "service" not in data or "price" not in data:
        return jsonify({"error": "Datos incompletos"}), 400

    service_name = data["service"]
    price = int(float(data["price"]) * 100)  # Stripe usa centavos

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
            success_url=f"https://asistente-virtual-may-roga.onrender.com/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url="https://asistente-virtual-may-roga.onrender.com/cancel",
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Opcional: endpoints de éxito y cancelación
@app.route("/success")
def success():
    return "Pago realizado correctamente. Gracias por usar Asistente Virtual May Roga."

@app.route("/cancel")
def cancel():
    return "Pago cancelado. Puedes intentar de nuevo."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
