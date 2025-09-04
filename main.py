import os
import json
import sys
import threading
import queue
from datetime import datetime
from flask import Flask, jsonify, request, render_template
import stripe
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
import time

app = Flask(__name__)

# --- Stripe ---
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
if not stripe.api_key:
    print("Error: 'STRIPE_SECRET_KEY' no configurada.", file=sys.stderr)
    sys.exit(1)

productos = {
    'rapida': {'price_id': 'price_1OaX6qBOA5mT4t0PLXz7r7k5', 'name': 'Agente de Respuesta Rápida'},
    'risoterapia': {'price_id': 'price_1OaX7LBOA5mT4t0P4Lz7d7e8', 'name': 'Risoterapia y Bienestar Natural'},
    'horoscopo': {'price_id': 'price_1OaX8lBOA5mT4t0PHaVpQW8d', 'name': 'Horóscopo'}
}

# --- Firebase ---
firebase_config_json = os.environ.get('__firebase_config__')
if firebase_config_json:
    try:
        cred = credentials.Certificate(json.loads(firebase_config_json))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase inicializado correctamente.")
    except Exception as e:
        print(f"Error inicializando Firebase: {e}", file=sys.stderr)
else:
    print("Error: '__firebase_config__' no configurada.", file=sys.stderr)

# --- Gemini ---
gemini_api_key = os.environ.get('GEMINI_API_KEY')
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    print("Gemini configurado correctamente.")
else:
    print("Error: 'GEMINI_API_KEY' no configurada.", file=sys.stderr)

# --- Cola de chat ---
chat_queue = queue.Queue()
responses_cache = {}
USER_LIMIT = 3  # máximo de solicitudes simultáneas por usuario

# --- Stripe Checkout ---
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.get_json()
        service_id = data.get('serviceId')
        if service_id not in productos:
            return jsonify({"error": "Servicio no válido"}), 400

        product = productos[service_id]
        success_url = request.url_root + f'success?service={service_id}'
        cancel_url = request.url_root + 'cancel'

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': product['price_id'], 'quantity': 1}],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return jsonify({'id': session.id})
    except Exception as e:
        print(f"Error Stripe: {e}", file=sys.stderr)
        return jsonify({"error": "Error interno del servidor"}), 500

# --- Endpoints web ---
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/success')
def success():
    return render_template("success.html")

@app.route('/cancel')
def cancel():
    return render_template("cancel.html")

# --- Chat ---
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_id = data.get('userId', 'anon')
        message = data.get('message', '').strip()
        if not message:
            return jsonify({"error": "No se recibió mensaje"}), 400

        # Limitar solicitudes por usuario
        user_count = sum(1 for item in list(chat_queue.queue) if item['user_id'] == user_id)
        if user_count >= USER_LIMIT:
            return jsonify({"error": "Has alcanzado el límite de solicitudes simultáneas. Intenta más tarde."}), 429

        # Añadir a cola
        response_event = threading.Event()
        chat_queue.put({'user_id': user_id, 'message': message, 'event': response_event})
        response_event.wait(timeout=15)
        reply_text = responses_cache.pop(user_id, "Lo siento, hubo un error procesando tu solicitud.")
        return jsonify({"reply": reply_text})

    except Exception as e:
        print(f"Error chat endpoint: {e}", file=sys.stderr)
        return jsonify({"error": "Error interno del servidor"}), 500

# --- Procesar cola en hilo ---
def process_queue():
    while True:
        try:
            item = chat_queue.get()
            user_id = item['user_id']
            message = item['message']

            system_prompt = """
You are May Roga Assistant, professional wellness guide using TVid techniques.
Listen without judgment, validate feelings, reflect user words, suggest small actions, offer hope.
Short clear answers 30-90 seconds, warm tone, safe health advice.
Detect language automatically.
"""
            reply_text = "Error procesando Gemini."
            if gemini_api_key:
                try:
                    response = genai.chat.create(
                        model="chat-bison-001",
                        messages=[{"role": "system", "content": system_prompt},
                                  {"role": "user", "content": message}],
                        temperature=0.7
                    )
                    reply_text = response.last.response
                except Exception as e:
                    print(f"Error Gemini: {e}", file=sys.stderr)

            # Guardar en Firebase
            if firebase_config_json:
                try:
                    db.collection("chat_history").add({
                        "user_id": user_id,
                        "message": message,
                        "reply": reply_text,
                        "timestamp": datetime.utcnow()
                    })
                except Exception as e:
                    print(f"Error guardando Firebase: {e}", file=sys.stderr)

            responses_cache[user_id] = reply_text
            item['event'].set()
            chat_queue.task_done()
            time.sleep(0.5)
        except Exception as e:
            print(f"Error procesando cola: {e}", file=sys.stderr)

threading.Thread(target=process_queue, daemon=True).start()

# --- Ejecutar app ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
