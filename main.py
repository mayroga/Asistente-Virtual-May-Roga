import os
import json
import stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore
from google.generativeai import TextGenerationClient, text
from gtts import gTTS
from io import BytesIO
import base64

app = FastAPI()

# CORS
origins = [os.getenv("URL_SITE", "https://asistente-virtual-may-roga.onrender.com")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")

# Firestore
firebase_config = json.loads(os.getenv("__firebase_config__"))
db = firestore.Client.from_service_account_info(firebase_config)

# Gemini/OpenAI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Código secreto
MAYROGA_ACCESS_CODE = os.getenv("MAYROGA_ACCESS_CODE")

# Servicios
SERVICES = {
    "Risoterapia y Bienestar Natural": {"duration": 600, "price": 1200},
    "Horóscopo y Consejos de Vida": {"duration": 120, "price": 600},
    "Respuesta Rápida": {"duration": 55, "price": 200},
    "Servicio Personalizado": {"duration": 1200, "price": 5000},
    "Servicio Corporativo": {"duration": 1500, "price": 75000},
    "Servicio Grupal": {"duration": 900, "price": 45000},
}

@app.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    data = await request.json()
    product = data.get("product")
    amount = data.get("amount")

    if not product or not amount:
        raise HTTPException(status_code=400, detail="Producto o monto faltante")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": product},
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=os.getenv("URL_SITE") + "/success.html",
            cancel_url=os.getenv("URL_SITE") + "/cancel.html",
        )
        return {"id": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assistant-stream")
async def assistant_stream(service: str, secret: str = None):
    # Verificar acceso
    access_granted = False
    if secret and secret.strip() == MAYROGA_ACCESS_CODE:
        access_granted = True
    elif service not in SERVICES:
        raise HTTPException(status_code=400, detail="Servicio no válido")

    # Generar respuesta
    prompt = f"Usuario solicitó: {service}. Aplicar TVid, dualidad positivo/negativo, voz clara y motivadora."

    # Llamada a Gemini/OpenAI
    try:
        client = TextGenerationClient(api_key=GEMINI_API_KEY)
        response = client.generate_text(
            model="gemini-1.5-t",
            prompt=prompt,
            max_output_tokens=500
        )
        text_response = response.result
    except Exception:
        text_response = f"[Asistente May Roga]: Lo siento, no pude generar la respuesta para {service}."

    # Generar TTS
    tts_audio = gTTS(text_response, lang="es")  # detecta automáticamente idioma si lo deseas cambiar
    mp3_fp = BytesIO()
    tts_audio.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")

    return JSONResponse({
        "access": "granted" if access_granted else "user",
        "text": text_response,
        "audio": audio_base64
    })

@app.get("/config")
def get_config():
    return {"stripe_key": STRIPE_PUBLISHABLE_KEY}

