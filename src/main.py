from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import stripe
import os

app = FastAPI()

# Si no tienes carpeta static, comentar la siguiente línea
# app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Configura tu clave secreta de Stripe aquí
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # mejor ponerla en Render como variable de entorno

# Precios de los servicios (en centavos)
PRECIOS = {
    "asistente_virtual": 500,
    "risoterapia": 1200,
    "horoscopo": 300
}

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/create-checkout-session")
async def create_checkout_session(apodo: str = Form(...), servicio: str = Form(...)):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': servicio
                    },
                    'unit_amount': PRECIOS.get(servicio, 500),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{os.getenv('SITE_URL')}?apodo={apodo}&servicio={servicio}",
            cancel_url=f"{os.getenv('SITE_URL')}",
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.post("/get-service")
async def get_service(apodo: str = Form(...), servicio: str = Form(...)):
    resultado = ""
    if servicio == "asistente_virtual":
        resultado = "Asistente Virtual (informativo, 8 minutos) listo para atenderte."
    elif servicio == "risoterapia":
        resultado = "Risoterapia basada en Técnicas de Vida, 10 minutos."
    elif servicio == "horoscopo":
        resultado = "Horóscopo 35 segundos, consejos zodiacales."
    else:
        resultado = "Servicio no reconocido."
    return JSONResponse({"resultado": resultado})

@app.post("/chat")
async def chat(apodo: str = Form(...), message: str = Form(...)):
    # Respuesta simulada del asistente, mínima para ahorrar tokens
    respuesta = f"Hola {apodo}, recibí tu mensaje: '{message}'. Te responderé de forma breve y profesional."
    return JSONResponse({"respuesta": respuesta})
