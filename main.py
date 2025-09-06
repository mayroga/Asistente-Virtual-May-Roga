from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import stripe

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# --- Configuración Stripe ---
stripe.api_key = "sk_live_TU_CLAVE_SECRETA"  # Cambia por tu clave secreta
PUBLIC_KEY = "pk_live_51NqPxQBOA5mT4t0PEoRVRc0Sj7DugiHvxhozC3BYh0q0hAx1N3HCLJe4xEp3MSuNMA6mQ7fAO4mvtppqLodrtqEn00pgJNQaxz"

# --- RUTA PRINCIPAL: sirve el index.html ---
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
            success_url='https://asistente-virtual-may-roga.onrender.com/success',
            cancel_url='https://asistente-virtual-may-roga.onrender.com/cancel',
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- Unlock servicios con código secreto ---
@app.route('/assistant-unlock', methods=['POST'])
def unlock_services():
    data = request.get_json()
    secret = data.get('secret')
    if secret == "MICHA991775":  # tu código secreto
        return jsonify({'success': True})
    return jsonify({'success': False})

# --- SSE para el asistente ---
@app.route('/assistant-stream')
def assistant_stream():
    from flask import Response
    import time

    service = request.args.get('service', 'Servicio')
    secret = request.args.get('secret', None)

    def generate():
        # ejemplo de mensajes de prueba
        messages = [
            f"Bienvenido al {service}!",
            "Aquí empieza tu sesión de bienestar...",
            "Disfruta de la experiencia 😊"
        ]
        for msg in messages:
            yield f"data: {msg}|\n\n"
            time.sleep(1)
    return Response(generate(), mimetype='text/event-stream')

# --- Rutas de éxito y cancelación de pago ---
@app.route('/success')
def success():
    return "Pago exitoso ✅"

@app.route('/cancel')
def cancel():
    return "Pago cancelado ❌"

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
