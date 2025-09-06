import os
import json
from flask import Flask, jsonify, request, redirect, Response
from flask_cors import CORS
import stripe
from time import sleep

app = Flask(__name__)
CORS(app)

# --- Endpoint para la ruta principal ---
# Esto resuelve el error 404 y proporciona una página de inicio.
@app.route("/")
def home():
    return "¡Hola! Tu servicio de Asistente Virtual está en funcionamiento."

# Configuración de Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
YOUR_DOMAIN = os.environ.get("URL_SITE")

# Variables de entorno importantes
ACCESS_CODE = os.environ.get("MAYROGA_ACCESS_CODE")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# --- Endpoint para config segura ---
@app.route("/config")
def get_config():
    return jsonify({
        "STRIPE_PUBLISHABLE_KEY": os.environ.get("STRIPE_PUBLISHABLE_KEY"),
        "URL_SITE": YOUR_DOMAIN
    })

# --- Endpoint para desbloqueo con código secreto ---
@app.route("/assistant-unlock", methods=["POST"])
def unlock_services():
    data = request.json
    if data.get("secret") == ACCESS_CODE:
        return jsonify({"success": True})
    return jsonify({"success": False}), 403

# --- Crear sesión de pago con Stripe ---
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': data['product'],
                    },
                    'unit_amount': int(data['amount']*100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
        return jsonify({"id": session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

# --- SSE para el asistente (texto y audio simulado) ---
@app.route("/assistant-stream")
def assistant_stream():
    service = request.args.get("service")
    secret = request.args.get("secret")

    # Validar código secreto si se solicita "all"
    if service == "all" and secret != ACCESS_CODE:
        return "Forbidden", 403

    def event_stream():
        messages = [
            f"Iniciando servicio: {service}",
            "Procesando tus datos...",
            "Servicio en curso, disfruta de la experiencia.",
            "Finalizando sesión, gracias por usar Asistente May Roga."
        ]
        for msg in messages:
            sleep(2)  # simula tiempo de procesamiento
            yield f"data:{msg}|\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

# --- Webhook de Stripe (opcional) ---
@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except Exception as e:
        return str(e), 400
    # Aquí se podrían procesar pagos completados
    return "", 200

# --- Ejecutar ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
