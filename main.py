from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import stripe
import asyncio
import os
import json
import httpx
import firebase_admin
from firebase_admin import credentials, firestore

# -----------------------------
# CONFIGURACIÓN INICIAL
# -----------------------------
app = Flask(__name__)
CORS(app, origins=["https://asistente-virtual-may-roga.onrender.com", "https://yoursite.com"])  # tu URL_SITE

# Variables de entorno
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRECT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIREBASE_CONFIG = os.getenv("__firebase_config__")
MAYROGA_ACCESS_CODE = os.getenv("MAYROGA_ACCESS_CODE")

stripe.api_key = STRIPE_SECRET_KEY

# Firebase
cred = credentials.Certificate(json.loads(FIREBASE_CONFIG))
firebase_admin.initialize_app(cred)
db = firestore.client()

# Servicios y duración en segundos
SERVICES = {
    "Risoterapia y Bienestar Natural": 600,
    "Horóscopo y Consejos de Vida": 120,
    "Respuesta Rápida": 55,
    "Servicio Personalizado": 1200,
    "Servicio Corporativo": 1200,  # promedio
    "Servicio Grupal": 900
}

# -----------------------------
# ENDPOINTS
# -----------------------------

# Crear sesión Stripe
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.json
    product = data.get("product")
    amount = int(data.get("amount"))
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": product},
                    "unit_amount": amount
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"{os.getenv('URL_SITE')}/success.html",
            cancel_url=f"{os.getenv('URL_SITE')}/cancel.html"
        )
        return jsonify({"id": session.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Obtener duración del servicio
@app.route("/get-duration")
def get_duration():
    service = request.args.get("service")
    duration = SERVICES.get(service, 300)
    return jsonify({"duration": duration})

# SSE con TTS y mensajes en vivo
@app.route("/assistant-stream")
def assistant_stream():
    service = request.args.get("service")
    secret = request.args.get("secret")

    # Validar acceso por código secreto
    if secret and secret == MAYROGA_ACCESS_CODE:
        access_granted = True
    elif service not in SERVICES:
        return jsonify({"access": "denied"}), 403
    else:
        access_granted = False

    async def generate_events():
        messages = [
            f"Bienvenido al servicio {service}.",
            "Aplicando Técnicas de Vida (TVid)...",
            "Escuchando tu estado y adaptando la sesión...",
            "Sesión en progreso..."
        ]

        # Simular IA y TTS en vivo
        for msg in messages:
            # Llamada a OpenAI/Gemini TTS para generar audio
            audio_url = await generate_tts(msg)
            yield f"data: {msg}\n\n"
            if audio_url:
                yield f"data: 🎵{audio_url}\n\n"
            await asyncio.sleep(2)

    return Response(generate_events(), mimetype="text/event-stream")

# -----------------------------
# FUNCIONES AUXILIARES
# -----------------------------

async def generate_tts(text):
    """
    Genera TTS con Gemini/OpenAI según el idioma detectado automáticamente
    Retorna URL de audio listo para reproducir
    """
    # Detección de idioma automática (simple, se puede mejorar)
    import langdetect
    lang = "es"  # predeterminado
    try:
        from langdetect import detect
        lang = detect(text)
    except:
        pass

    # Llamada ficticia a API TTS Gemini/OpenAI
    # Aquí se puede integrar la API real de Gemini/OpenAI TTS
    # Se devuelve una URL pública accesible desde el frontend
    # Para fines de prueba, podemos devolver un audio local o un placeholder
    return f"https://asistente-virtual-may-roga.onrender.com/static/tts_placeholder.mp3"

# Guardar historial en Firebase
def save_message(user_id, service, message, response):
    doc_ref = db.collection("chats").document(user_id)
    doc_ref.set({
        "service": service,
        "message": message,
        "response": response
    }, merge=True)

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
