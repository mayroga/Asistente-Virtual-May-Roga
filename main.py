from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import stripe
import os
import openai
import json

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# --- Claves desde variables de entorno ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
PUBLIC_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
MAYROGA_SECRET = os.environ.get("MAYROGA_ACCESS_CODE")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
URL_SITE = os.environ.get("URL_SITE")  # Para success/cancel URLs

openai.api_key = OPENAI_API_KEY

# --- Home ---
@app.route("/")
def home():
    return render_template("index.html", stripe_public_key=PUBLIC_KEY)

# --- Desbloquear servicios con código secreto ---
@app.route("/assistant-unlock", methods=["POST"])
def unlock():
    data = request.json
    if data.get("secret") == MAYROGA_SECRET:
        return jsonify({"success": True})
    return jsonify({"success": False})

# --- Crear sesión de pago Stripe ---
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': data['product']},
                    'unit_amount': int(float(data['amount']) * 100)
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=f"{URL_SITE}/success?service={data['product']}",
            cancel_url=f"{URL_SITE}/cancel"
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --- Generar respuesta OpenAI ---
@app.route("/assistant-stream-message", methods=["POST"])
def assistant_stream_message():
    data = request.json
    service = data.get("service")
    messages = data.get("messages", [])
    
    if not messages:
        return jsonify({"answer": "No se envió ningún mensaje."})
    
    # Construir prompt
    prompt = f"""Eres el Asistente May Roga, creado por Maykel Rodríguez García. 
Atiendes con risoterapia, bienestar natural y técnicas TVid. 
Servicio seleccionado: {service}.
Usuario: {messages[-1]}
Asistente:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error AI: {str(e)}"})

# --- Páginas de éxito y cancelación ---
@app.route("/success")
def success():
    service = request.args.get("service", "")
    return f"✅ Pago exitoso. Servicio activado: {service}"

@app.route("/cancel")
def cancel():
    return "❌ Pago cancelado."

# --- Ejecutar ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
