# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import stripe
import os
import openai

app = FastAPI()

# Archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configuración Stripe y OpenAI
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "tu_clave_secreta_stripe")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "tu_clave_publica_stripe")
stripe.api_key = STRIPE_SECRET_KEY
openai.api_key = os.getenv("OPENAI_API_KEY", "tu_clave_openai")

# Servicios disponibles y precios en USD
SERVICES = {
    "medico": 5,
    "risoterapia": 7,
    "horoscopo": 3
}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "services": SERVICES, "stripe_public_key": STRIPE_PUBLIC_KEY}
    )

@app.post("/create-checkout-session")
async def create_checkout_session(service: str = Form(...), nickname: str = Form(...)):
    if service not in SERVICES:
        return JSONResponse({"error": "Servicio no válido"}, status_code=400)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(SERVICES[service]*100),
                    "product_data": {"name": f"{service} - {nickname}"}
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"https://medico-virtual-may-roga.onrender.com/?success=true&nickname={nickname}&service={service}",
            cancel_url="https://medico-virtual-may-roga.onrender.com/?canceled=true"
        )
        return JSONResponse({"url": checkout_session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/chat")
async def chat_endpoint(data: dict):
    message = data.get("message")
    nickname = data.get("nickname")
    service = data.get("service")

    if not message or not nickname or not service:
        return JSONResponse({"reply": "Falta información para procesar tu solicitud."})

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Servicio: {service}, Apodo: {nickname}, Mensaje: {message}"}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = "Error generando respuesta: " + str(e)

    return JSONResponse({"reply": reply})
