from flask import Flask, render_template, request, jsonify, redirect
import os
import stripe

app = Flask(__name__)

# Claves de Stripe desde variables de entorno
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
ACCESS_CODE = os.environ.get('MAYROGA_ACCESS_CODE')

# Página principal
@app.route('/')
def index():
    return render_template('index.html', stripe_key=STRIPE_PUBLISHABLE_KEY, access_code=ACCESS_CODE)

# Endpoint para crear sesión de pago
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.json
    try:
        # Datos del servicio desde el cliente
        service_name = data['service']
        price = int(data['price'] * 100)  # Stripe usa centavos

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': service_name,
                    },
                    'unit_amount': price,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=os.environ.get('SUCCESS_URL', 'https://asistente-virtual-may-roga.onrender.com/success'),
            cancel_url=os.environ.get('CANCEL_URL', 'https://asistente-virtual-may-roga.onrender.com/cancel'),
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify(error=str(e)), 403

# Página de éxito
@app.route('/success')
def success():
    return "¡Pago completado con éxito! Gracias por tu compra."

# Página de cancelación
@app.route('/cancel')
def cancel():
    return "Pago cancelado. Puedes intentar de nuevo."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
