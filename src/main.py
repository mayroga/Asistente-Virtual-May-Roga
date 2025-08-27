from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import stripe
import os

app = FastAPI()

# Configuración Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")  # Render manejará la variable de entorno

templates = Jinja2Templates(directory="templates")

# ENDPOINT PRINCIPAL
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# CREATE CHECKOUT SESSION
@app.post("/create-checkout-session")
async def create_checkout_session(apodo: str = Form(...), servicio: str = Form(...)):
    try:
        # Montos simples para ejemplo
        amount_map = {"asistente_virtual": 500, "risoterapia": 1200, "horoscopo": 300}
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {
                "currency": "usd",
                "unit_amount": amount_map.get(servicio, 500),
                "product_data": {"name": servicio.replace("_"," ").title()},
            },
            "quantity": 1}],
            mode="payment",
            success_url=os.environ.get("SUCCESS_URL")+"?apodo="+apodo+"&servicio="+servicio,
            cancel_url=os.environ.get("CANCEL_URL"),
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)})

# CHAT
@app.post("/chat")
async def chat(request: Request):
    form = await request.form()
    apodo = form.get("apodo")
    message = form.get("message")
    # Aquí conectas con OpenAI o lógica offline
    respuesta = f"Respuesta generada para '{apodo}': tu mensaje '{message}' ha sido recibido por Asistente Virtual Médico."
    return JSONResponse({"respuesta": respuesta})
