from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import stripe
import os

app = FastAPI()

# Configura CORS si tu web lo necesita
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates = Jinja2Templates(directory="templates")

# --- QUITAMOS ESTA LÍNEA QUE CAUSABA EL ERROR ---
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Stripe API Key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Crear sesión de pago
@app.post("/create-checkout-session")
async def create_checkout_session(apodo: str = Form(...), servicio: str = Form(...)):
    try:
        # Define los precios según el servicio
        precios = {
            "asistente_virtual": 500,   # $5.00
            "risoterapia": 1200,        # $12.00
            "horoscopo": 300            # $3.00
        }
        amount = precios.get(servicio, 500)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"{servicio} - {apodo}",
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"https://medico-virtual-may-roga.onrender.com?apodo={apodo}&servicio={servicio}",
            cancel_url="https://medico-virtual-may-roga.onrender.com",
        )
        return JSONResponse({"url": checkout_session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)})

# Obtener servicio después del pago
@app.post("/get-service")
async def get_service(apodo: str = Form(...), servicio: str = Form(...)):
    resultados = {
        "asistente_virtual": "Tu Asistente Virtual está listo para comenzar.",
        "risoterapia": "Tu sesión de Risoterapia ha comenzado.",
        "horoscopo": "Tu horóscopo personalizado está listo."
    }
    return JSONResponse({"resultado": resultados.get(servicio, "Servicio no encontrado.")})

# Chat con asistente
@app.post("/chat")
async def chat(apodo: str = Form(...), message: str = Form(...)):
    # Aquí puedes poner tu lógica de respuestas
    respuesta = f"Hola {apodo}, recibí tu mensaje: '{message}'."
    return JSONResponse({"respuesta": respuesta})
