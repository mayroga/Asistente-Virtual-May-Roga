import os
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from flask import Flask, jsonify, request
import stripe # Importa la librería de Stripe
import json
import sys
import requests
from datetime import datetime

# Crea la instancia de la aplicación Flask
app = Flask(__name__)

# --- Configuración de Stripe ---
# Obtiene la clave secreta de Stripe de una variable de entorno
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

if not stripe.api_key:
    print("Error: La variable de entorno 'STRIPE_SECRET_KEY' no está configurada.", file=sys.stderr)
    sys.exit(1)

# Los productos y sus precios, coincidiendo con los del frontend
productos = {
    'rapida': {
        'price_id': 'price_1OaX6qBOA5mT4t0PLXz7r7k5', # Sustituye con el Price ID real de Stripe
        'name': 'Agente de Respuesta Rápida'
    },
    'risoterapia': {
        'price_id': 'price_1OaX7LBOA5mT4t0P4Lz7d7e8', # Sustituye con el Price ID real de Stripe
        'name': 'Risoterapia y Bienestar Natural'
    },
    'horoscopo': {
        'price_id': 'price_1OaX8lBOA5mT4t0PHaVpQW8d', # Sustituye con el Price ID real de Stripe
        'name': 'Horóscopo'
    }
}

# --- Configuración de Firebase ---
# Obtiene la configuración de Firebase de la variable de entorno
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

# --- Configuración de la API de Gemini ---
# Obtiene la clave de API de Gemini de la variable de entorno
gemini_api_key = os.environ.get('GEMINI_API_KEY')

if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    print("Cliente de la API de Gemini configurado correctamente.")
else:
    print("Error: La variable de entorno 'GEMINI_API_KEY' no está configurada.", file=sys.stderr)

# --- Rutas de la aplicación (endpoints) ---
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

        # URL de la página de éxito y la página de cancelación
        success_url = request.url_root + '?payment_status=success'
        cancel_url = request.url_root + '?payment_status=cancel'

        # Crea la sesión de pago de Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': product['price_id'],
                'quantity': 1,
            }],
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
