import os
import json
import stripe
from flask import Flask, jsonify, request, redirect, render_template
from flask_cors import CORS
from google.generativeai import GenerativeModel
import google.ai.generativelanguage as glm

# Cargar variables de entorno y configuración
try:
    __firebase_config__ = os.environ.get('__firebase_config__')
    if __firebase_config__:
        firebase_config = json.loads(__firebase_config__)
    else:
        # En caso de no estar en Canvas, se usarán valores por defecto
        raise ValueError("FIREBASE_CONFIG environment variable is not set.")
    
    stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
    url_site = os.environ.get('URL_SITE')
    gemini_api_key = os.environ.get('GEMINI_API_KEY')

    if not stripe_secret_key:
        raise ValueError("STRIPE_SECRET_KEY environment variable is not set.")
    if not url_site:
        raise ValueError("URL_SITE environment variable is not set.")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    stripe.api_key = stripe_secret_key
    glm.configure(api_key=gemini_api_key)

except (ValueError, json.JSONDecodeError) as e:
    print(f"Error en la configuración de las variables de entorno: {e}")
    stripe_secret_key = "sk_test_..."
    url_site = "http://localhost:5000"
    gemini_api_key = "YOUR_GEMINI_API_KEY"
    stripe.api_key = stripe_secret_key
    glm.configure(api_key=gemini_api_key)


app = Flask(__name__, template_folder='templates')
CORS(app)

# === Rutas para el Frontend ===

@app.route('/')
def home():
    """Sirve el archivo HTML principal de la aplicación."""
    # Ahora servimos el archivo may_roga_chat_assistant.html
    return render_template('may_roga_chat_assistant.html')


# Productos y precios
PRODUCTS = {
    'risoterapia': { 'price': 1200, 'name': 'Risoterapia' },
    'rapida': { 'price': 200, 'name': 'Asesoría Rápida' },
    'horoscopo': { 'price': 500, 'name': 'Horóscopo' },
}

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.json
    service = data.get('service')
    
    if service not in PRODUCTS:
        return jsonify(error="Servicio no encontrado"), 404
        
    product_data = PRODUCTS[service]

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product_data['name'],
                    },
                    'unit_amount': product_data['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_site + '/success',
            cancel_url=url_site + '/cancel',
        )
        return jsonify({'sessionId': checkout_session.id})

    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Maneja las interacciones del chat con la API de Gemini."""
    try:
        data = request.json
        user_message = data.get('user_message')
        chat_history = data.get('chat_history', [])

        if not user_message:
            return jsonify({'error': 'No se proporcionó un mensaje.'}), 400

        model = GenerativeModel('gemini-2.5-flash-preview-05-20')
        
        # Iniciar el chat con el historial
        chat_session = model.start_chat(history=chat_history)
        response = chat_session.send_message(user_message)

        return jsonify({'assistant_message': response.text})

    except Exception as e:
        print(f"Error en la ruta del chat: {e}")
        return jsonify({'error': 'Error interno del servidor al procesar el mensaje.'}), 500


@app.route('/success')
def success():
    return "Pago Exitoso. Volver a la aplicación."

@app.route('/cancel')
def cancel():
    return "Pago Cancelado. Volver a la aplicación."

if __name__ == '__main__':
    app.run(debug=True)
