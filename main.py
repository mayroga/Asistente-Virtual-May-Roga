import os
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from flask import Flask, jsonify, request
import stripe
import json
import sys
from datetime import datetime

# --- Inicialización de Flask ---
app = Flask(__name__)

# --- Configuración de Stripe ---
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
if not stripe.api_key:
    print("Error: La variable de entorno 'STRIPE_SECRET_KEY' no está configurada.", file=sys.stderr)
    sys.exit(1)

# Productos y precios (coinciden con frontend)
productos = {
    'rapida': {'price_id': 'price_1OaX6qBOA5mT4t0PLXz7r7k5', 'name': 'Agente de Respuesta Rápida'},
    'risoterapia': {'price_id': 'price_1OaX7LBOA5mT4t0P4Lz7d7e8', 'name': 'Risoterapia y Bienestar Natural'},
    'horoscopo': {'price_id': 'price_1OaX8lBOA5mT4t0PHaVpQW8d', 'name': 'Horóscopo'}
}

# --- Configuración de Firebase ---
firebase_config_json = os.environ.get('__firebase_config__')
if firebase_config_json:
    try:
        cred = credentials.Certificate(json.loads(firebase_config_json))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase inicializado correctamente.")
    except Exception as e:
        print(f"Error al inicializar Firebase: {e}", file=sys.stderr)
else:
    print("Error: La variable de entorno '__firebase_config__' no está configurada.", file=sys.stderr)

# --- Configuración de Gemini ---
gemini_api_key = os.environ.get('GEMINI_API_KEY')
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    print("Cliente de la API de Gemini configurado correctamente.")
else:
    print("Error: La variable de entorno 'GEMINI_API_KEY' no está configurada.", file=sys.stderr)

# --- Endpoints ---

@app.route('/')
def home():
    return jsonify({
        "status": "éxito",
        "mensaje": "La aplicación está funcionando correctamente. Las APIs de Firebase, Gemini y Stripe están configuradas."
    })


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.get_json()
        service_id = data.get('serviceId')
        if service_id not in productos:
            return jsonify({"error": "Servicio no válido"}), 400

        product = productos[service_id]
        success_url = request.url_root + '?payment_status=success'
        cancel_url = request.url_root + '?payment_status=cancel'

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': product['price_id'], 'quantity': 1}],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return jsonify({'id': checkout_session.id})
    except stripe.error.StripeError as e:
        print(f"Error de Stripe: {e}", file=sys.stderr)
        return jsonify(error=str(e)), 403
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        return jsonify(error="Error inesperado en el servidor"), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        user_language = data.get('language', 'auto')

        if not user_message:
            return jsonify({"error": "No se recibió mensaje"}), 400

        # Prompt de May Roga Assistant
        system_prompt = """
You are May Roga Assistant, a professional wellness guide specialized in Laughter Therapy and Natural Wellness.
Follow the TVid techniques: Bien, Mal, Padre, Madre, Niño, Beso, Guerra.
Core ethic: listen without judgment, never shame or contradict; reflect the client's words and guide to healthy, responsible choices.
Always balance negative and positive to turn duality into growth, calm, and wellbeing.
Use clear, short answers (30–90 seconds), concrete steps, and a warm tone.
Avoid medical diagnoses or prescriptions; offer general health education, prevention, exercise and nutrition advice within safe limits.
Encourage responsible follow-up with professionals when needed.
Detect language automatically if not specified.
For each response: 
1) validate feelings
2) choose one TVid lens and name it
3) give one small actionable step
4) provide one hopeful takeaway
        """

        # --- Llamada a Gemini ---
        if gemini_api_key:
            response = genai.chat.create(
                model="chat-bison-001",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
            )
            reply_text = response.last.response
        else:
            reply_text = "Error: Gemini API key no configurada."

        return jsonify({"reply": reply_text})

    except Exception as e:
        print(f"Error en /api/chat: {e}", file=sys.stderr)
        return jsonify({"error": "Error interno del servidor"}), 500


# --- Arranque de la app ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
