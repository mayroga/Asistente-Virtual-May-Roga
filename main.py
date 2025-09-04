# app.py
import os
from flask import Flask, request, jsonify
import stripe

app = Flask(__name__)

# --- Stripe Configuración ---
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # tu clave secreta en Render

# Precios fijos de tus servicios
SERVICES = {
    "Respuesta Rápida": 200,  # $2.00 en centavos
    "Risoterapia y Bienestar Natural": 1200,  # $12.00 en centavos
    "Horóscopo y Consejos": 500,  # $5.00 en centavos
    "Sesión Risoterapia 20min": 2000,  # $20.00
    "Sesión Personalizada 30min": 3500,  # $35.00
    "Paquete Corporativo 20-40min": 5000  # $50.00
}

# --- Ruta para crear sesión de pago ---
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        data = request.json
        service_name = data.get("service")
        amount = SERVICES.get(service_name)

        if amount is None:
            return jsonify({"error": "Servicio no válido"}), 400

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
            success_url="https://asistente-virtual-may-roga.onrender.com/success",
            cancel_url="https://asistente-virtual-may-roga.onrender.com/cancel",
        )

        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify(error=str(e)), 500


# --- Ruta para validar código secreto ---
@app.route("/validate-access-code", methods=["POST"])
def validate_access_code():
    try:
        data = request.json
        user_code = data.get("access_code")
        secret_code = os.getenv("ACCESS_CODE")  # código guardado en Render

        if user_code == secret_code:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    except Exception as e:
        return jsonify(error=str(e)), 500


# --- Rutas de prueba ---
@app.route("/success")
def success():
    return "✅ Pago realizado con éxito. Gracias por confiar en May Roga."

@app.route("/cancel")
def cancel():
    return "❌ El pago fue cancelado. Intenta de nuevo."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
