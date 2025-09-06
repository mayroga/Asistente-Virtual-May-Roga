from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import stripe
import os
import time
import openai
from google.generativeai import TextGenerationClient
from google.auth import credentials

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# --- Configuración Stripe ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
PUBLIC_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")

# --- Configuración OpenAI ---
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- Configuración Google Gemini ---
gemini_api_key = os.environ.get("GEMINI_API_KEY")
gemini_client = TextGenerationClient(credentials=gemini_api_key)

# --- Código secreto ---
ACCESS_CODE = os.environ.get("MAYROGA_ACCESS_CODE")

# --- RUTA PRINCIPAL ---
@app.route('/')
def index():
    return render_template('index.html', stripe_public_key=PUBLIC_KEY)

# --- Crear sesión de checkout Stripe ---
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout():
    data = request.get_json()
    product = data.get('product')
    amount = data.get('amount')

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': product},
                    'unit_amount': int(amount*100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=os.environ.get("URL_SITE") + '/success',
            cancel_url=os.environ.get("URL_SITE") + '/cancel',
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- Desbloquear servicios con código secreto ---
@app.route('/assistant-unlock', methods=['POST'])
def unlock_services():
    data = request.get_json()
    secret = data.get('secret')
    if secret == ACCESS_CODE:
        return jsonify({'success': True})
    return jsonify({'success': False})

# --- SSE para chat dinámico del asistente ---
@app.route('/assistant-stream')
def assistant_stream():
    service = request.args.get('service', 'Servicio')
    secret = request.args.get('secret', None)
    initial_message = request.args.get('message', '')

    def generate():
        messages = [f"Iniciando sesión de {service}..."]
        for msg in messages:
            yield f"data: {msg}|\n\n"
            time.sleep(1)

        # --- Generación dinámica con IA ---
        for _ in range(5):  # 5 mensajes de ejemplo por servicio
            response_text = generate_ai_response(service, initial_message)
            yield f"data: {response_text}|\n\n"
            time.sleep(2)

        yield f"data: Sesión de {service} finalizada ✅|\n\n"

    return Response(generate(), mimetype='text/event-stream')

# --- Función para generar respuesta inteligente según servicio ---
def generate_ai_response(service_name, user_message):
    prompt = f"Actúa como Asistente May Roga. Servicio: {service_name}. Responde de manera positiva, profesional y personalizada a este mensaje: {user_message}"

    # --- OpenAI GPT ---
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150
        )
        text = response['choices'][0]['message']['content'].strip()
        return text
    except Exception as e:
        return f"[Error AI: {str(e)}]"

# --- Rutas de éxito y cancelación de pago ---
@app.route('/success')
def success():
    return "Pago exitoso ✅"

@app.route('/cancel')
def cancel():
    return "Pago cancelado ❌"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
