import os
import stripe
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI
import time

# Cargar variables de entorno
load_dotenv()

# Configurar claves de API de Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Configurar API de Google Gemini (Flash)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configurar API de OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, static_url_path='/static')

# --- Rutas de la API ---

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/static/css/<path:path>')
def serve_css(path):
    return send_from_directory('static/css', path)

@app.route('/static/js/<path:path>')
def serve_js(path):
    return send_from_directory('static/js', path)

@app.route('/config')
def get_config():
    # Enviar la clave pública de Stripe al frontend
    return jsonify({
        'publicKey': os.getenv('STRIPE_PUBLIC_KEY')
    })

@app.route('/access-code', methods=['POST'])
def check_access_code():
    code = request.form.get('code')
    if code == "MAYROGA2024":
        return jsonify({'message': 'Acceso concedido. ¡Bienvenido a tu sesión!'})
    else:
        return jsonify({'error': 'Código de acceso incorrecto. Por favor, inténtalo de nuevo.'}), 401

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    service = request.form.get('service')
    apodo = request.form.get('apodo')

    prices = {
        'respuesta_rapida': 100,  # $1.00 USD en centavos
        'risoterapia': 1200,      # $12.00 USD en centavos
        'horoscopo': 300          # $3.00 USD en centavos
    }

    price = prices.get(service)
    if not price:
        return jsonify(error="Servicio no válido."), 400

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Servicio de {service.replace("_", " ").title()}',
                        },
                        'unit_amount': price,
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url='http://127.0.0.1:5000/success',
            cancel_url='http://127.0.0.1:5000/cancel',
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 500

# Endpoint para manejar eventos de webhook de Stripe
@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    # Manejar el evento
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Aquí puedes manejar la lógica de negocio después del pago
        # Por ejemplo: actualizar tu base de datos, enviar un correo, etc.
        print("Pago exitoso. ID de la sesión:", session.id)

    return 'OK', 200


@app.route('/chat', methods=['POST'])
def chat():
    apodo = request.form.get('apodo')
    service = request.form.get('service')
    message = request.form.get('message')
    lang = request.form.get('lang')

    # Prompt base para el asistente
    # Este prompt determina el comportamiento del asistente May Roga.
    # Puede ser dinámico y basarse en el servicio.
    base_prompt = """
    Eres el Médico Virtual May Roga. Tu propósito es ayudar a las personas a encontrar bienestar a través del humor, la risa y un enfoque holístico. Tu tono es divertido, alegre, motivacional y ligeramente místico. Debes utilizar las "Técnicas de Vida (TVid)" en tus respuestas, como la Técnica del Niño (TDN), la Técnica del Bien (TDB) y la Técnica del Amor (TDA).

    Instrucciones específicas para cada servicio:
    - Agente de Respuesta Rápida: Ofrece consejos breves y generales sobre salud, nutrición o ejercicio. Usa la Técnica del Bien (TDB) para fomentar hábitos positivos. Duración máxima: 55 segundos.
    - Risoterapia y Bienestar Natural: Ofrece una respuesta más elaborada, con un enfoque en la risa y el humor. Usa la Técnica del Niño (TDN) para reconectar con la alegría interior. Duración máxima: 10 minutos.
    - Horóscopo Motivacional: Da un consejo positivo y motivacional basado en el horóscopo (sin mencionar un signo específico). Usa la Técnica del Amor (TDA) para inspirar el autoconocimiento y la compasión. Duración máxima: 90 segundos.

    No te refieras a ti mismo como una IA o modelo de lenguaje.
    Mantén un tono positivo y esperanzador.
    Responde en el mismo idioma que el usuario.
    Tus respuestas son educativas e informativas, nunca sustituyen una consulta médica profesional. Recuérdalo al final de cada respuesta.
    """

    full_prompt = f"{base_prompt}\n\nMensaje del usuario ({apodo}): {message}\n\nEn base al servicio '{service}', responde con el estilo de May Roga:"
    
    try:
        # Se podría implementar una lógica para elegir entre Gemini y OpenAI.
        # Por ahora, se utiliza Gemini de forma predeterminada para el chat.
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        text_response = response.text
        
        # Simular la generación de audio (TTS)
        # En una aplicación real, se usaría un servicio de TTS.
        # Por ejemplo, la API de Gemini TTS o un servicio externo.
        # Aquí solo se simula la respuesta de texto.
        
        # Retraso para simular el procesamiento
        time.sleep(1)

        # Retornar la respuesta como JSON
        return jsonify({'text': text_response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
