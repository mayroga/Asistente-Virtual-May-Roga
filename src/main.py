# src/main.py
from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import os
import openai
import stripe

# Configuración Render y Stripe
app = FastAPI()
templates = Jinja2Templates(directory="templates")

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
SECRET_CODE_NAME = "MKM991775"

stripe.api_key = STRIPE_SECRET_KEY

# Montaje de carpeta estática opcional (solo si usas CSS/JS)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Simulación de "cerebro offline"
OFFLINE_MEMORY = {}

# Página principal
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "stripe_key": STRIPE_PUBLISHABLE_KEY})

# Acceso directo con código secreto
@app.post("/access-secret")
async def access_secret(apodo: str = Form(...), code: str = Form(...)):
    if code.strip().upper() == SECRET_CODE_NAME:
        OFFLINE_MEMORY[apodo] = {"active": True}
        return JSONResponse({"success": True, "message": f"Acceso concedido para {apodo}. Ya puedes usar el Asistente Virtual Médico, Risoterapia y Horóscopo."})
    return JSONResponse({"success": False, "message": "Código secreto incorrecto."})

# Crear sesión de pago Stripe
@app.post("/create-checkout-session")
async def create_checkout_session(apodo: str = Form(...), servicio: str = Form(...)):
    # Diccionario de precios
    prices = {
        "asistente_virtual": 500,  # en centavos
        "risoterapia": 1200,
        "horoscopo": 300
    }
    price = prices.get(servicio)
    if not price:
        return JSONResponse({"error": "Servicio inválido."})

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': servicio},
                    'unit_amount': price,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{os.environ.get('FRONTEND_URL')}?apodo={apodo}&servicio={servicio}",
            cancel_url=f"{os.environ.get('FRONTEND_URL')}",
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)})

# Chat con asistente (OpenAI + backup offline)
@app.post("/chat")
async def chat(apodo: str = Form(...), message: str = Form(...)):
    if apodo not in OFFLINE_MEMORY or not OFFLINE_MEMORY[apodo].get("active"):
        return JSONResponse({"respuesta": "Debes usar el código secreto o pagar para acceder al servicio."})

    # Intentar OpenAI
    try:
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres Asistente Virtual Médico, Risoterapia y Horóscopo, basado en técnicas de vida de May Roga LLC."},
                {"role": "user", "content": message}
            ],
            temperature=0.7
        )
        respuesta = completion.choices[0].message.content
    except Exception:
        # Backup offline simple
        respuesta = f"Respuesta generada para '{apodo}': tu mensaje '{message}' ha sido recibido por Asistente Virtual Médico."

    return JSONResponse({"respuesta": respuesta})
