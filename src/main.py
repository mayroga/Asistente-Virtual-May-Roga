# main.py
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import stripe
import openai

# -----------------------------
# Configuración de claves
# -----------------------------
os.environ["OPENAI_API_KEY"] = "TU_OPENAI_API_KEY"  # Tu API Key de OpenAI
SECRET_ACCESS_CODE = "MKM991775"  # Código secreto para acceso gratis

stripe.api_key = "TU_STRIPE_SECRET_KEY"  # Tu clave privada Stripe

# -----------------------------
# Inicialización FastAPI
# -----------------------------
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# -----------------------------
# Servicios disponibles
# -----------------------------
services = {
    "medico_virtual": {"name": "Asistente Virtual Médico", "price": 5},
    "risoterapia": {"name": "Risoterapia y Bienestar Natural", "price": 5},
    "horoscopo": {"name": "Horóscopo y Bienestar Natural", "price": 3},
}

# -----------------------------
# Rutas principales
# -----------------------------
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "services": services})

# -----------------------------
# Cobro con Stripe
# -----------------------------
@app.post("/create-checkout-session")
async def create_checkout_session(apodo: str = Form(...), service: str = Form(...)):
    if service not in services:
        return JSONResponse({"error": "Servicio no válido"}, status_code=400)
    
    price = int(services[service]["price"] * 100)  # en centavos
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": services[service]["name"]},
                    "unit_amount": price,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://TU_DOMINIO/success",
            cancel_url="https://TU_DOMINIO/cancel",
            metadata={"apodo": apodo, "service": service},
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# -----------------------------
# Chat con OpenAI
# -----------------------------
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    apodo = data.get("apodo")
    mensaje = data.get("mensaje")
    access_code = data.get("access_code", "")

    # Validación: pago o código secreto
    if access_code != SECRET_ACCESS_CODE and not data.get("paid", False):
        return JSONResponse({"respuesta": "Acceso denegado. Pago o código secreto requerido."})

    # Generar respuesta básica (puedes mejorar con GPT)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": mensaje}]
        )
        respuesta = response.choices[0].message.content
    except Exception:
        respuesta = f"(ASISTENTE_VIRTUAL) Respuesta para '{apodo}': recibí tu mensaje: '{mensaje}'. Por ahora respondo en modo básico. Si hay urgencia, atención presencial."
    
    return {"respuesta": respuesta}
