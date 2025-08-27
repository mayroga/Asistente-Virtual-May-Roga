from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import stripe
import os

app = FastAPI()

# Configuración de Stripe
stripe.api_key = "TU_STRIPE_SECRET_KEY"  # <-- Cambia por tu clave secreta de Stripe

# Carpeta de templates y static
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Servicios y precios
SERVICIOS = {
    "asistente_virtual": {"nombre": "Asistente Virtual", "precio": 500},
    "risoterapia": {"nombre": "Risoterapia", "precio": 1200},
    "horoscopo": {"nombre": "Horóscopo", "precio": 300},
}

# Página principal
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Crear sesión de pago Stripe
@app.post("/create-checkout-session")
async def create_checkout_session(apodo: str = Form(...), servicio: str = Form(...)):
    if not apodo.strip():
        return JSONResponse({"error": "Apodo obligatorio"})
    if servicio not in SERVICIOS:
        return JSONResponse({"error": "Servicio no válido"})
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": SERVICIOS[servicio]["nombre"]},
                    "unit_amount": SERVICIOS[servicio]["precio"],
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{os.getenv('SITE_URL','http://localhost:8000')}?apodo={apodo}&servicio={servicio}",
            cancel_url=f"{os.getenv('SITE_URL','http://localhost:8000')}",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)})

# Mostrar servicio después del pago
@app.post("/get-service")
async def get_service(apodo: str = Form(...), servicio: str = Form(...)):
    if servicio not in SERVICIOS:
        return JSONResponse({"resultado": "Servicio no válido"})
    return JSONResponse({"resultado": f"{SERVICIOS[servicio]['nombre']} activo y listo para {apodo}"})

# Chat con asistente virtual
@app.post("/chat")
async def chat(apodo: str = Form(...), message: str = Form(...)):
    # Aquí se puede conectar con tu lógica de IA o respuestas predefinidas
    respuesta = f"Hola {apodo}, recibí tu mensaje: {message}. (Respuesta generada por Asistente Virtual Medico)"
    return JSONResponse({"respuesta": respuesta})
