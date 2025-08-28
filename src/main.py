from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import openai
import stripe
import os

# Cargar claves de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Tu clave secreta real

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Código secreto para acceso gratuito
FREE_CODE = "MKM991775"

# Precios y duración de servicios
SERVICIOS = {
    "medico": {"precio": 5, "duracion": 8, "nombre": "Asistente Virtual Médico"},
    "risoterapia": {"precio": 12, "duracion": 10, "nombre": "Risoterapia y Bienestar Natural"},
    "horoscopo": {"precio": 3, "duracion": 1.5, "nombre": "Horóscopo"}
}

# Pagos activos
pagos_confirmados = {}

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "servicios": SERVICIOS})

@app.post("/chat")
async def chat(
    apodo: str = Form(...),
    servicio: str = Form(...),
    mensaje: str = Form(...),
    pago: str = Form(None),
    code: str = Form(None)
):
    acceso = False
    if pago == "true":
        acceso = True
    if code == FREE_CODE:
        acceso = True

    if not acceso:
        return JSONResponse({"respuesta": "Acceso denegado. Debes pagar o usar un código válido."})

    if servicio not in SERVICIOS:
        return JSONResponse({"respuesta": "Servicio no válido."})

    try:
        # Chat inteligente según servicio
        system_prompt = ""
        if servicio == "medico":
            system_prompt = "Eres un asistente médico profesional. Responde con precisión y cuidado."
        elif servicio == "risoterapia":
            system_prompt = "Eres un instructor de risoterapia basado en las Técnicas de Vida (Tvid) de May Roga. Incluye ejercicios prácticos."
        elif servicio == "horoscopo":
            system_prompt = "Eres un astrólogo profesional. Da horóscopos breves y precisos."

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje}
            ],
            max_tokens=400
        )
        respuesta_texto = response.choices[0].message.content.strip()
        return JSONResponse({"respuesta": respuesta_texto})

    except Exception as e:
        return JSONResponse({"respuesta": f"Error: {str(e)}"})

@app.post("/crear-sesion-stripe")
async def crear_sesion_stripe(servicio: str = Form(...), apodo: str = Form(...)):
    if servicio not in SERVICIOS:
        return JSONResponse({"error": "Servicio inválido"})
    precio = SERVICIOS[servicio]["precio"] * 100  # en centavos
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": SERVICIOS[servicio]["nombre"]},
                    "unit_amount": precio
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"https://TU_DOMINIO/render.com?apodo={apodo}&servicio={servicio}&pago=true",
            cancel_url=f"https://TU_DOMINIO/render.com"
        )
        return JSONResponse({"id": session.id})
    except Exception as e:
        return JSONResponse({"error": str(e)})
