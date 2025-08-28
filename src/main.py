from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import openai
import stripe
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuración de Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Configuración OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Carpeta de templates y static
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Código secreto para acceso gratuito
FREE_CODE = os.getenv("FREE_CODE", "MKM991775")

# Servicios disponibles
SERVICES = {
    "medico": "Asistente Virtual Médico",
    "risoterapia": "Risoterapia y Bienestar Natural",
    "horoscopo": "Horóscopo"
}

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "services": SERVICES})

@app.post("/chat")
async def chat(
    request: Request,
    apodo: str = Form(...),
    servicio: str = Form(...),
    mensaje: str = Form(...),
    code: str = Form(None),
    pago_confirmado: bool = Form(False)
):
    # Verificar acceso
    if not pago_confirmado and code != FREE_CODE:
        return JSONResponse({"error": "Acceso no autorizado. Paga o usa código secreto."})

    # Mensaje para OpenAI según servicio
    if servicio == "medico":
        system_prompt = "Eres un médico virtual, responde de manera profesional y segura. Si hay urgencia, indica atención presencial."
    elif servicio == "risoterapia":
        system_prompt = "Eres un experto en risoterapia y bienestar natural. Proporciona consejos útiles y positivos."
    elif servicio == "horoscopo":
        system_prompt = "Eres un astrólogo que da horóscopos y consejos de bienestar diario."
    else:
        system_prompt = "Eres un asistente virtual que da respuestas informativas."

    # Crear respuesta con OpenAI Chat API nueva
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{apodo}: {mensaje}"}
        ],
        temperature=0.7,
        max_tokens=300
    )

    answer = response.choices[0].message["content"]

    return JSONResponse({"respuesta": answer})

@app.post("/create-payment-intent")
async def create_payment_intent(amount: int = Form(...)):
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd"
        )
        return JSONResponse({"client_secret": intent.client_secret})
    except Exception as e:
        return JSONResponse({"error": str(e)})
