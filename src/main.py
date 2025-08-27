from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import stripe
import os

# Stripe key
stripe.api_key = "TU_STRIPE_SECRET_KEY"

app = FastAPI()

# Templates
templates = Jinja2Templates(directory="templates")

# No usamos StaticFiles para evitar errores de carpeta
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Código secreto válido
CODIGO_SECRETO = "MKM991775"

# Página principal
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Crear sesión de pago Stripe
@app.post("/create-checkout-session")
async def create_checkout_session(
    request: Request,
    apodo: str = Form(...),
    servicio: str = Form(...)
):
    if not apodo:
        return JSONResponse({"error": "Debes ingresar un apodo"})
    
    # Lógica de precios
    precios = {
        "asistente_virtual": 500,  # $5 en centavos
        "risoterapia": 1200,       # $12
        "horoscopo": 300           # $3
    }
    precio = precios.get(servicio, 0)

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": servicio},
                    "unit_amount": precio,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{request.url.scheme}://{request.url.hostname}?apodo={apodo}&servicio={servicio}",
            cancel_url=f"{request.url.scheme}://{request.url.hostname}",
        )
        return JSONResponse({"url": checkout_session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)})

# Obtener servicio después del pago
@app.post("/get-service")
async def get_service(apodo: str = Form(...), servicio: str = Form(...)):
    mensajes_servicio = {
        "asistente_virtual": "Acceso completo al Asistente Virtual Médico",
        "risoterapia": "Sesión de Risoterapia y Bienestar Natural",
        "horoscopo": "Tu Horóscopo personalizado"
    }
    resultado = mensajes_servicio.get(servicio, "Servicio no encontrado")
    return JSONResponse({"resultado": resultado})

# Chat con Asistente Virtual
@app.post("/chat")
async def chat(apodo: str = Form(...), message: str = Form(...)):
    # Aquí puedes integrar la lógica real de AI o respuestas predefinidas
    respuesta = f"{apodo}, recibí tu mensaje: '{message}'. Pronto recibirás tu asistencia."
    return JSONResponse({"respuesta": respuesta})

# Validación de código secreto al iniciar el servicio
@app.post("/start-service")
async def start_service(apodo: str = Form(...), codigo: str = Form(...), servicio: str = Form(...)):
    if codigo.lower() != CODIGO_SECRETO.lower():
        return JSONResponse({"error": "Código secreto incorrecto"})
    return JSONResponse({"resultado": f"Bienvenido {apodo}, comenzando tu servicio: {servicio}"})
