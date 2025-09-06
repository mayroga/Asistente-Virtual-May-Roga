# main.py definitivo - Asistente May Roga 🌿
import os
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import stripe
import httpx
from google.cloud import firestore
from google.generativeai import TextToSpeechClient

# ---------- Variables de entorno ----------
FIREBASE_CONFIG = os.getenv("__firebase_config__")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRECT")
URL_SITE = os.getenv("URL_SITE")
MAYROGA_ACCESS_CODE = os.getenv("MAYROGA_ACCESS_CODE", "TU_CODIGO_SECRETO_ADMIN")  # solo tu lo conoces

stripe.api_key = STRIPE_SECRET_KEY

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[URL_SITE],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------- Firestore (historial de chat) ----------
db = firestore.Client.from_service_account_info(json.loads(FIREBASE_CONFIG))
chat_collection = db.collection("chat_history")

# ---------- Duraciones en segundos ----------
SERVICES_DURATION = {
    "Risoterapia y Bienestar Natural": 600,
    "Horóscopo y Consejos de Vida": 120,
    "Respuesta Rápida": 55,
    "Servicio Personalizado": 1200,
    "Servicio Corporativo": 1200,  # duración de 1 sesión, puede multiplicarse
    "Servicio Grupal": 900
}

# ---------- Crear sesión Stripe ----------
@app.post("/create-checkout-session")
async def create_checkout_session(req: Request):
    data = await req.json()
    product = data.get("product")
    amount = int(data.get("amount", 0)) * 100  # centavos
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data':{
                    'currency':'usd',
                    'product_data':{'name': product},
                    'unit_amount': amount
                },
                'quantity':1
            }],
            mode='payment',
            success_url=f"{URL_SITE}/success.html",
            cancel_url=f"{URL_SITE}/cancel.html"
        )
        return JSONResponse({"id": session.id})
    except Exception as e:
        return JSONResponse({"error": str(e)})

# ---------- Obtener duración ----------
@app.get("/get-duration")
async def get_duration(service: str):
    duration = SERVICES_DURATION.get(service, 300)
    return {"duration": duration}

# ---------- SSE Mensajes en vivo con TTS ----------
@app.get("/assistant-stream")
async def assistant_stream(service: str, secret: str = None):
    # Acceso con código secreto
    if secret == MAYROGA_ACCESS_CODE:
        access_granted = True
    else:
        access_granted = False

    async def event_generator():
        messages = []
        if service == "all" and access_granted:
            messages.append("🎉 Acceso completo desbloqueado por el administrador.")
            messages.append("Listo para usar todos los servicios de May Roga LLC.")
        else:
            messages.append(f"Bienvenido al servicio {service}.")
            messages.append("Aplicando técnicas TVid y dualidad positiva/negativa...")
            messages.append("Escuchando tu estado y adaptando la sesión...")

        for msg in messages:
            # Generar TTS con Gemini/OpenAI
            audio_url = await generate_tts(msg)
            yield f"data: 🎵{audio_url}\n\n"  # indica que es audio clicable
            yield f"data: {msg}\n\n"
            await asyncio.sleep(2)

    headers = {"Content-Type": "text/event-stream", "Cache-Control": "no-cache"}
    return StreamingResponse(event_generator(), headers=headers)

# ---------- Función TTS ----------
async def generate_tts(text: str) -> str:
    """
    Genera un audio TTS usando Gemini/OpenAI.
    Retorna la URL pública de un mp3 temporal.
    """
    # Aquí usamos Gemini TTS como ejemplo
    try:
        client = TextToSpeechClient(api_key=GEMINI_API_KEY)
        voice_config = {
            "languageCode": "auto",  # detecta idioma
            "name": "all-natural-voice"
        }
        input_text = {"text": text}
        response = client.synthesize_speech(
            input=input_text,
            voice=voice_config,
            audio_config={"audioEncoding":"MP3"}
        )
        # Guardar audio en /static/audios con nombre temporal
        filename = f"static/audios/{int(asyncio.get_event_loop().time()*1000)}.mp3"
        with open(filename, "wb") as f:
            f.write(response.audio_content)
        # Retornar ruta relativa para que el front pueda reproducirlo
        return f"/{filename}"
    except Exception as e:
        print("Error TTS:", e)
        return ""  # si falla, solo texto

# ---------- Historial en Firebase ----------
@app.post("/save-message")
async def save_message(req: Request):
    data = await req.json()
    chat_collection.add(data)
    return {"status":"ok"}

# ---------- Inicio rápido ----------
@app.get("/")
async def root():
    return JSONResponse({"message":"Asistente May Roga listo para producción ✅"})

# ---------- Webhook Stripe (opcional) ----------
@app.post("/webhook")
async def stripe_webhook(req: Request):
    payload = await req.body()
    sig_header = req.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        # Aquí puedes manejar pagos exitosos si quieres
        return JSONResponse({"status":"success"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
