from flask import Flask, render_template, request, jsonify 
from flask_cors import CORS
import stripe
import os
import openai

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
# --- Configuración CORS para Google Sites ---
CORS(app, origins=["https://sites.google.com"]) 

# --- Configuración de llaves del entorno ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
PUBLIC_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
MAYROGA_SECRET = os.environ.get("MAYROGA_ACCESS_CODE")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")  # Solo si usarás Gemini
URL_SITE = os.environ.get("URL_SITE")

openai.api_key = OPENAI_API_KEY

# --- Ruta principal ---
@app.route('/')
def index():
    return render_template('index.html', stripe_public_key=PUBLIC_KEY)

# --- Crear sesión de pago Stripe ---
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
                    'unit_amount': int(amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{URL_SITE}/success?service={product}',
            cancel_url=f'{URL_SITE}/cancel',
        )
        return jsonify({'url': session.url})   # ✅ ahora devuelve la URL
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- Desbloquear servicios con código secreto ---
@app.route('/assistant-unlock', methods=['POST'])
def unlock_services():
    data = request.get_json()
    secret = data.get('secret')
    if secret == MAYROGA_SECRET:
        return jsonify({'success': True})
    return jsonify({'success': False})

# --- Generar respuesta de IA dinámica ---
@app.route('/assistant-stream', methods=['GET'])
def assistant_stream():
    service = request.args.get('service', 'Servicio')
    message = request.args.get('message', '')

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": 
                 """Eres Asistente May Roga, creado por Maykel Rodríguez García, experto en risoterapia y bienestar natural.
                 Conoces todas las Técnicas de Vida (Tvid): TDB, TDM, TDN, TDK, TDP, TDMM, TDG.
                 Explica siempre qué son, para qué sirven, ejemplos, cómo se aplican en cada servicio y por qué se usan.
                 Integra dualidad positiva/negativa en tus respuestas y utiliza ejercicios de Tvid cuando sea posible.
                 Responde con tono profesional, cálido, empático y cercano, y adapta ejemplos según la edad y situación del usuario."""},
                {"role": "user", "content": message}
            ]
        )
        answer = response.choices[0].message.content
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'answer': f"Error al generar respuesta: {str(e)}"})

# --- Nuevo endpoint para recibir mensajes en tiempo real ---
@app.route('/assistant-stream-message', methods=['POST'])
def assistant_stream_message():
    data = request.get_json()
    service = data.get('service', 'Servicio')
    messages = data.get('messages', [])

    try:
        formatted_messages = [
            {"role": "system", "content": 
             """Eres Asistente May Roga, creado por Maykel Rodríguez García, experto en risoterapia y bienestar natural.
             Conoces todas las Técnicas de Vida (Tvid): TDB, TDM, TDN, TDK, TDP, TDMM, TDG.
             Explica siempre qué son, para qué sirven, ejemplos, cómo se aplican en cada servicio y por qué se usan.
             Integra dualidad positiva/negativa en tus respuestas y utiliza ejercicios de Tvid cuando sea posible.
             Siempre escucha primero, respeta tiempos de ejercicios y responde en el idioma del cliente.
             Responde con tono profesional, cálido, empático y cercano, adaptando ejemplos a la situación y edad del usuario."""}
        ]
        for m in messages:
            formatted_messages.append({"role": "user", "content": m})

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=formatted_messages
        )
        answer = response.choices[0].message.content
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'answer': f"Error al generar respuesta: {str(e)}"})

# --- Rutas de éxito y cancelación de pago ---
@app.route('/success')
def success():
    service = request.args.get('service', '')
    return f"Pago exitoso ✅. Servicio activado: {service}"

@app.route('/cancel')
def cancel():
    return "Pago cancelado ❌"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
