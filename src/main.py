# src/main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import stripe
import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Configuración API keys
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Static y Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Servicios disponibles
SERVICES = {
    "asistente": {"name": "Asistente Virtual Médico", "price": 5, "time": 8},
    "risoterapia": {"name": "Sesión de Risoterapia", "price": 7, "time": 10},
    "horoscopo": {"name": "Horóscopo Personalizado", "price": 3, "time": 5},
}

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "services": SERVICES})

@app.post("/create-payment-intent")
async def create_payment_intent(
    amount: int = Form(...),
    currency: str = Form("usd")
):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # USD a centavos
            currency=currency
        )
        return JSONResponse({"client_secret": intent.client_secret})
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_msg = data.get("message", "")
    apodo = data.get("nickname", "Usuario")
    service = data.get("service", "asistente")

    if service not in SERVICES:
        return JSONResponse({"reply": "Servicio no válido."})

    prompt = f"Servicio: {SERVICES[service]['name']}\nUsuario ({apodo}): {user_msg}\nRespuesta:"
    
    try:
        # OpenAI nueva sintaxis >=1.0.0
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente virtual médico, risoterapia y horóscopo. Responde con claridad y de forma amigable."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Error en la respuesta del asistente: {str(e)}"

    return JSONResponse({"reply": answer})
