from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import stripe
import time
import asyncio

app = FastAPI()
stripe.api_key = "TU_STRIPE_SECRET_KEY"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Duraciones por servicio en segundos
SERVICES_DURATION = {
    "Risoterapia y Bienestar Natural": 600,
    "Horóscopo y Consejos de Vida": 120,
    "Respuesta Rápida": 55,
    "Servicio Personalizado": 1200,
    "Paquete VIP": 2400
}

@app.post("/create-checkout-session")
async def create_checkout_session(req: Request):
    data = await req.json()
    product = data.get("product")
    amount = data.get("amount") * 100  # centavos
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price_data':{'currency':'usd','product_data':{'name':product},'unit_amount':amount}, 'quantity':1}],
            mode='payment',
            success_url="https://tusitio.com/success.html",
            cancel_url="https://tusitio.com/cancel.html"
        )
        return JSONResponse({"id": session.id})
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.get("/get-duration")
async def get_duration(service: str, secret: str = None):
    duration = SERVICES_DURATION.get(service, 300)
    return {"duration": duration}

@app.get("/assistant-stream")
async def assistant_stream(service: str, secret: str = None):
    async def event_generator():
        messages = [
            f"Bienvenido al servicio {service}.",
            "Aplicando Técnicas de Vida (TVid)...",
            "Escuchando tu estado y adaptando la sesión...",
            "Sesión en progreso..."
        ]
        for msg in messages:
            yield f"data: {msg}\n\n"
            await asyncio.sleep(2)
    return JSONResponse(content=event_generator())
