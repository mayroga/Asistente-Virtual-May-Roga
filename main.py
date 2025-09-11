from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import stripe
import os
import openai

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# --- Claves ---
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY")
MAYROGA_SECRET = os.environ.get("MAYROGA_ACCESS_CODE")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
URL_SITE = os.environ.get("URL_SITE")

openai.api_key = OPENAI_API_KEY

# --- Servicios completos ---
SERVICIOS = [
    {"name":"Risoterapia y Bienestar Natural","price":8,"duration":300},
    {"name":"Servicio Express","price":3,"duration":48},
    {"name":"HOROSCOPO Y CONSEJOS DE VIDA","price":6,"duration":80},
    {"name":"Té Mágico en 2 Minutos","price":3.99,"duration":120},
    {"name":"Infusión Anti-Estrés","price":5.99,"duration":120},
    {"name":"Batido Energético Natural","price":3.99,"duration":120},
    {"name":"Mini Guía de Plantas Curativas","price":3.99,"duration":120},
    {"name":"Respiración Verde Express","price":3.99,"duration":120},
    {"name":"Risa Relámpago","price":3.99,"duration":120},
    {"name":"Motívate en un Minuto","price":3.99,"duration":90},
    {"name":"Respira y Sonríe","price":3.99,"duration":120},
    {"name":"Confianza Express","price":5.99,"duration":120},
    {"name":"Optimismo al Instante","price":3.99,"duration":60},
    {"name":"Horóscopo Flash","price":3.99,"duration":60},
    {"name":"Consejo del Día","price":5.99,"duration":90},
    {"name":"Amor Instantáneo","price":3.99,"duration":60},
    {"name":"Abundancia en 2 Minutos","price":5.99,"duration":120},
    {"name":"Mensaje de tu Estrella","price":3.99,"duration":120},
    {"name":"Mini Diagnóstico de Hábitos","price":3.99,"duration":120},
    {"name":"Ejercicio TVid Express","price":3.99,"duration":120},
    {"name":"Prevención en un Minuto","price":5.99,"duration":60},
    {"name":"Reto 3 Días Express","price":5.99,"duration":120},
    {"name":"Tracker de Bienestar Diario","price":3.99,"duration":60},
    {"name":"Receta Verde Express","price":3.99,"duration":120},
    {"name":"Té Relajante Rápido","price":5.99,"duration":120},
    {"name":"Batido Creativo","price":3.99,"duration":120},
    {"name":"Infusión para Claridad Mental","price":5.99,"duration":120},
    {"name":"Mini Detox Express","price":3.99,"duration":120}
]

# --- Funciones OpenAI ---
def generar_respuesta_openai(service, messages):
    try:
        formatted = [{"role":"system","content":f"Eres Asistente May Roga, guía de {service}."}]
        for m in messages:
            formatted.append({"role":"user","content":m})
        resp = openai.chat.completions.create(model="gpt-4", messages=formatted)
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error AI: {str(e)}"

# --- Rutas ---
@app.route("/")
def home():
    return render_template("index.html", stripe_public_key=PUBLIC_KEY)

@app.route("/assistant-unlock", methods=["POST"])
def unlock():
    data = request.json
    return jsonify({"success": data.get("secret") == MAYROGA_SECRET})

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    product_name = data['product']
    amount = int(float(data['amount'])*100)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {'currency':'usd','product_data':{'name':product_name},'unit_amount':amount},
                'quantity':1
            }],
            mode='payment',
            success_url=f"{URL_SITE}/success?service={product_name}",
            cancel_url=f"{URL_SITE}/cancel"
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}),400

@app.route("/assistant-stream-message", methods=["POST"])
def assistant_stream_message():
    data = request.json
    service = data.get("service")
    messages = data.get("messages", [])
    if not messages: return jsonify({"answer":"No se envió mensaje."})
    answer = generar_respuesta_openai(service, messages)
    return jsonify({"answer": answer})

@app.route("/success")
def success():
    service = request.args.get("service","")
    return f"✅ Pago exitoso. Servicio activado: {service}"

@app.route("/cancel")
def cancel():
    return "❌ Pago cancelado."

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
