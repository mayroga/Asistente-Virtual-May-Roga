import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import stripe

# Configuración Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")  # Tu clave privada en Render
endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")  # Variable de entorno segura

# Constantes de tu servicio
SECRET_CODE_NAME = "MKM991775"

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Montar carpeta static solo si existe
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    pass

# Página principal
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Crear checkout session
@app.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    form = await request.form()
    apodo = form.get("apodo")
    servicio = form.get("servicio")

    if not apodo or not servicio:
        return JSONResponse({"error": "Falta apodo o servicio"}, status_code=400)

    # Mapear precios
    precios = {
        "asistente_virtual": 500,
        "risoterapia": 1200,
        "horoscopo": 300
    }

    precio = precios.get(servicio)
    if precio is None:
        return JSONResponse({"error": "Servicio no válido"}, status_code=400)

    try:
        session = stripe.checkout.Session.create(
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
            success_url=f"{os.environ.get('APP_URL')}?apodo={apodo}&servicio={servicio}",
            cancel_url=os.environ.get('APP_URL'),
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Chat con asistente
@app.post("/chat")
async def chat(request: Request):
    form = await request.form()
    apodo = form.get("apodo")
    message = form.get("message")

    if not apodo or not message:
        return JSONResponse({"error": "Falta apodo o mensaje"}, status_code=400)

    # Simular respuesta del asistente (OpenAI u offline)
    respuesta = f"Respuesta generada para '{apodo}': tu mensaje '{message}' ha sido recibido por Asistente Virtual Médico."

    return JSONResponse({"respuesta": respuesta})

# Acceso directo con código secreto
@app.post("/secret-access")
async def secret_access(request: Request):
    form = await request.form()
    apodo = form.get("apodo")
    code = form.get("code")

    if not apodo or not code:
        return JSONResponse({"error": "Falta apodo o código"}, status_code=400)

    if code.upper() != SECRET_CODE_NAME:
        return JSONResponse({"error": "Código secreto incorrecto"}, status_code=403)

    return JSONResponse({
        "mensaje": f"Acceso concedido para {apodo}. Ya puedes usar el Asistente Virtual Médico, Risoterapia y Horóscopo."
    })

# Webhook de Stripe
@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if endpoint_secret is None:
        raise HTTPException(status_code=500, detail="Webhook secret no configurado")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Firma no válida")

    # Manejar evento exitoso de pago
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        apodo = session["metadata"].get("apodo", "Cliente")
        servicio = session["metadata"].get("servicio", "Servicio")
        print(f"Pago recibido: {apodo} - {servicio}")

    return JSONResponse({"status": "success"})
