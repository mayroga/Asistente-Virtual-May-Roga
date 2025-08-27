from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import stripe
import os

app = FastAPI(title="Asistente May Roga")

templates = Jinja2Templates(directory="templates")

# Stripe key from env
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Prices (cents)
PRECIOS = {
    "asistente_virtual": 500,
    "risoterapia": 1200,
    "horoscopo": 300
}

SITE_URL = os.getenv("SITE_URL", "https://medico-virtual-may-roga.onrender.com")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/create-checkout-session")
async def create_checkout_session(apodo: str = Form(...), servicio: str = Form(...)):
    if servicio not in PRECIOS:
        return JSONResponse({"error": "Servicio no válido"}, status_code=400)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": servicio},
                    "unit_amount": PRECIOS[servicio],
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{SITE_URL}?apodo={apodo}&servicio={servicio}",
            cancel_url=f"{SITE_URL}",
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/get-service")
async def get_service(apodo: str = Form(...), servicio: str = Form(...)):
    resultado = ""
    if servicio == "asistente_virtual":
        resultado = "Asistente Virtual Médico (informativo, 8 minutos) listo."
    elif servicio == "risoterapia":
        resultado = "Risoterapia y Bienestar (10 minutos) listo."
    elif servicio == "horoscopo":
        resultado = "Horóscopo (35 segundos) listo."
    else:
        resultado = "Servicio no reconocido."
    return JSONResponse({"resultado": resultado})

@app.post("/chat")
async def chat(apodo: str = Form(...), message: str = Form(...)):
    # Respuesta mínima para ahorrar tokens / simular asistente
    respuesta = f"Hola {apodo}, recibí: {message}. Respuesta breve y profesional (informativa)."
    return JSONResponse({"respuesta": respuesta})
