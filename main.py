import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
import stripe
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from openai import OpenAI

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# --- Inicialización de la aplicación Flask ---
app = Flask(__name__, static_folder='static')

# --- Configuración de Stripe ---
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe_public_key = os.getenv('STRIPE_PUBLIC_KEY')

# --- Configuración de las APIs de IA ---
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# --- Configuración de Firebase Firestore ---
# NOTA: En un entorno de producción, la credencial se almacenaría como una variable de entorno.
# Aquí se usa un archivo para la demostración.
try:
    cred = credentials.Certificate("firebase-service-account.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error al inicializar Firebase: {e}")
    db = None

# --- Datos de los servicios y precios (para Stripe) ---
# En un sistema real, esto se cargaría desde una base de datos.
SERVICIOS = {
    'respuesta_rapida': {
        'price_id': os.getenv('STRIPE_PRICE_ID_RAPIDA'),
        'name': 'Agente de Respuesta Rápida',
        'cost': 1.00,
        'ai_model': 'gemini'
    },
    'risoterapia': {
        'price_id': os.getenv('STRIPE_PRICE_ID_RISOTERAPIA'),
        'name': 'Risoterapia y Bienestar Natural',
        'cost': 12.00,
        'ai_model': 'openai'
    },
    'horoscopo': {
        'price_id': os.getenv('STRIPE_PRICE_ID_HOROSCOPO'),
        'name': 'Horóscopo Motivacional',
        'cost': 3.00,
        'ai_model': 'openai'
    }
}

# --- Rutas de la API (Endpoints) ---

@app.route('/config')
def get_config():
    """
    Ruta para enviar la clave pública de Stripe al frontend.
    """
    return jsonify({'publicKey': stripe_public_key})

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """
    Ruta para crear una sesión de pago con Stripe.
    """
    data = request.form
    apodo = data.get('apodo')
    servicio_id = data.get('service')

    if not apodo or not servicio_id or servicio_id not in SERVICIOS:
        return jsonify({'error': 'Datos de servicio o apodo no válidos.'}), 400

    servicio = SERVICIOS[servicio_id]
    
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price': servicio['price_id'],
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.url_root + f'/?apodo={apodo}&service={servicio_id}',
            cancel_url=request.url_root,
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/access-code', methods=['POST'])
def access_with_code():
    """
    Ruta para verificar un código de acceso. (Simulada)
    """
    data = request.form
    apodo = data.get('apodo')
    code = data.get('code')

    # Aquí iría la lógica para verificar el código en la base de datos
    # Por ahora, simulamos un código válido.
    if code == 'MAYROGA':
        return jsonify({'message': 'Acceso concedido. ¡Bienvenido a tu sesión!'})
    else:
        return jsonify({'error': 'Código de acceso incorrecto.'}), 401

@app.route('/chat', methods=['POST'])
def chat_with_assistant():
    """
    Ruta principal para la interacción con el asistente de IA.
    1. Recibe el mensaje.
    2. Enruta a la IA correcta.
    3. Genera la respuesta en texto.
    4. Convierte la respuesta a voz.
    5. Devuelve el audio al cliente.
    """
    data = request.form
    message = data.get('message')
    service = data.get('service')
    lang = data.get('lang')

    if not message or not service or not lang:
        return jsonify({'error': 'Faltan datos en la solicitud.'}), 400

    prompt_definitivo = f"""
        Tu rol es Asistente May Roga, asistente virtual creado por Maykel Rodríguez García. Tu misión es curar el espíritu y guiar al bienestar personal.
        Aplica siempre una de las Técnicas de Vida (TVid): del Bien, del Mal, del Padre, de la Madre, del Niño, del Beso o de la Guerra.
        Mantén un tono profesional, empático y de guía. Transforma siempre lo negativo en positivo, con un enfoque en la educación en salud, bienestar, nutrición y ejercicio.
        No des diagnósticos ni prescribas medicamentos. Siempre incluye un disclaimer al final de tu respuesta: "Este servicio es educativo, no sustituye la atención médica profesional."
        El idioma de la respuesta debe ser: {lang}
        El servicio actual es: {SERVICIOS[service]['name']}
        Mensaje del usuario: {message}
    """

    ai_response = ""
    try:
        # Lógica de enrutamiento de la IA
        if SERVICIOS[service]['ai_model'] == 'openai':
            completion = openai_client.chat.completions.create(
                model="gpt-4",  # O un modelo más económico como "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": prompt_definitivo},
                    {"role": "user", "content": message}
                ]
            )
            ai_response = completion.choices[0].message.content
        else: # Gemini
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt_definitivo, stream=False)
            ai_response = response.text

        # 2. Generar audio con Gemini TTS
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={os.getenv('GEMINI_API_KEY')}"
        payload = {
            "contents": [{"parts": [{"text": ai_response}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}
                }
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        audio_data = response.json()['candidates'][0]['content']['parts'][0]['inlineData']['data']
        # La lógica para convertir PCM a WAV se hará en el frontend
        return jsonify({'text': ai_response, 'audioData': audio_data}), 200

    except Exception as e:
        print(f"Error en la IA o en el TTS: {e}")
        return jsonify({'error': 'Lo siento, hubo un problema al procesar tu solicitud.'}), 500

# --- Rutas para servir los archivos estáticos ---
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/static/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('static/css', filename)

@app.route('/static/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('static/js', filename)

# --- Inicio del servidor ---
if __name__ == '__main__':
    # Para la demostración local, usamos debug=True. En producción, se usaría un servidor como Gunicorn.
    app.run(debug=True)
