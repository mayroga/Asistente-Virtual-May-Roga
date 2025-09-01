import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import openai
import stripe

# Configurar FastAPI
app = FastAPI()

# Configurar el directorio de archivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar el directorio de plantillas HTML
templates = Jinja2Templates(directory="templates")

# Configurar las claves de la API desde las variables de entorno de Render
openai.api_key = os.environ.get("OPENAI_API_KEY")
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

class ChatRequest(BaseModel):
    user_message: str
    nickname: str
    service: str

class PaymentRequest(BaseModel):
    service: str
    nickname: str

# Configuración de los servicios
SERVICES = {
    "respuesta_rapida": {"price": 100, "name": "Agente de Respuesta Rápida"},
    "risoterapia": {"price": 1200, "name": "Risoterapia y Bienestar Natural"},
    "horoscopo": {"price": 300, "name": "Horóscopo Motivacional"},
}

# --- Rutas de la aplicación ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat/", response_model=dict)
async def chat_with_assistant(chat_request: ChatRequest):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente de bienestar amable y servicial."},
                {"role": "user", "content": f"Conversación con {chat_request.nickname} sobre {chat_request.service}:\n{chat_request.user_message}"}
            ]
        )
        assistant_response = completion.choices[0].message.content
        return {"assistant_message": assistant_response}
    except Exception as e:
        return {"error": str(e)}

@app.post("/create-checkout-session/")
async def create_checkout_session(payment_request: PaymentRequest):
    service_info = SERVICES.get(payment_request.service)
    if not service_info:
        return {"error": "Servicio no válido"}

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': service_info["name"],
                    },
                    'unit_amount': service_info["price"],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://asistente-virtual-may-roga.onrender.com/?success=true',
            cancel_url='https://asistente-virtual-may-roga.onrender.com/?canceled=true',
        )
        return {"id": checkout_session.id}
    except Exception as e:
        return {"error": str(e)}
