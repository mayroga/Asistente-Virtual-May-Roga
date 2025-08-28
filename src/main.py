from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import stripe
import os
from dotenv import load_dotenv
import openai

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

SERVICES = {
    "respuesta_rapida": {"name": "Agente de Respuesta Rápida", "price": 1, "time": 55},
    "risoterapia": {"name": "Risoterapia y Bienestar Natural", "price": 12, "time": 10*60},
    "horoscopo": {"name": "Horóscopo", "price": 3, "time": 90}
}

ACCESS_CODES = os.getenv("ACCESS_CODES", "MKM991775").split(",")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "services": SERVICES})

@app.post("/chat")
async def chat(request: Request, apodo: str = Form(...), service: str = Form(...), message: str = Form(...), code: str = Form("")):
    # Verifica acceso
    if not ((code and code in ACCESS_CODES) or (apodo and apodo)):
        return JSONResponse({"error": "Acceso denegado"}, status_code=403)

    # Detectar servicio
    if service not in SERVICES:
        return JSONResponse({"error": "Servicio inválido"}, status_code=400)

    # Prompt según servicio
    if service == "respuesta_rapida":
        prompt = f"Eres un Agente de Respuesta Rápida educativo y profesional. Instrucciones: 55 segundos, $1, hablar sobre salud, risoterapia o horóscopo según el mensaje. Mensaje del usuario: {message}"
    elif service == "risoterapia":
        prompt = f"Eres un especialista en Risoterapia y Bienestar Natural según las Técnicas de Vida de May Roga LLC. Duración: 10 minutos, profesional, educativo. Mensaje del usuario: {message}"
    elif service == "horoscopo":
        prompt = f"Eres un astrólogo profesional y educativo. Horóscopo de 1 minuto 30 segundos. Mensaje del usuario: {message}"

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "No das diagnósticos ni recetas. Solo información educativa."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f"(Error al generar respuesta): {str(e)}"

    return JSONResponse({"reply": reply})

@app.post("/create-checkout-session")
async def create_checkout_session(service: str = Form(...), apodo: str = Form(...)):
    if service not in SERVICES:
        return JSONResponse({"error": "Servicio inválido"}, status_code=400)

    price = SERVICES[service]["price"] * 100  # centavos
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": "usd","product_data":{"name":SERVICES[service]["name"]},"unit_amount":price},"quantity":1}],
        mode="payment",
        success_url=f"{os.getenv('DOMAIN')}/?success=true&apodo={apodo}&service={service}",
        cancel_url=f"{os.getenv('DOMAIN')}/?canceled=true"
    )
    return JSONResponse({"id": session.id})
