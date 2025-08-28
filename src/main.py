import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import stripe
import openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configuración Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Tu clave secreta real
DOMAIN = os.getenv("DOMAIN")  # Dominio de tu web en Render

# Configuración OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Código secreto para acceso gratis
CODIGO_SECRETO = os.getenv("CODIGO_SECRETO")

# Servicios
SERVICIOS = {
    "agente_rapido": {"nombre": "Agente de Respuesta Rápida", "precio": 1, "duracion": "55s"},
    "risoterapia": {"nombre": "Risoterapia y Bienestar Natural", "precio": 12, "duracion": "10min"},
    "horoscopo": {"nombre": "Horóscopo", "precio": 3, "duracion": "1min30s"}
}

# Ruta principal
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "servicios": SERVICIOS})

# Crear sesión de pago Stripe
@app.post("/crear-checkout-session")
async def crear_checkout_session(servicio: str = Form(...), apodo: str = Form(...)):
    servicio_info = SERVICIOS.get(servicio)
    if not servicio_info:
        return JSONResponse({"error": "Servicio no válido"}, status_code=400)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(servicio_info["precio"] * 100),
                    "product_data": {"name": servicio_info["nombre"]},
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{DOMAIN}?success=true&apodo={apodo}&servicio={servicio}",
            cancel_url=f"{DOMAIN}?canceled=true",
        )
        return {"url": checkout_session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Chat con OpenAI
@app.post("/chat")
async def chat_service(apodo: str = Form(...), servicio: str = Form(...), mensaje: str = Form(...), code: str = Form(None)):
    # Validar acceso gratis por código secreto
    acceso_valido = False
    if code and code.strip() == CODIGO_SECRETO:
        acceso_valido = True
    # Para pago, se asume que frontend confirmó con Stripe
    # (podrías agregar verificación webhook si quieres total seguridad)
    if servicio not in SERVICIOS:
        return JSONResponse({"respuesta": "Servicio no válido."})
    if not acceso_valido and servicio == "agente_rapido":
        return JSONResponse({"respuesta": "Acceso denegado. Usa pago o código secreto."})

    # Generar prompt según servicio
    if servicio == "agente_rapido":
        prompt = f"Eres un Agente de Respuesta Rápida. Mensaje del usuario ({apodo}): {mensaje}. Responde solo con consejos de salud, risoterapia, bienestar o horóscopo. Sé breve, educativo, seguro, sin diagnósticos."
    elif servicio == "risoterapia":
        prompt = f"Eres un experto en Risoterapia y Bienestar Natural según las Técnicas de Vida de May Roga LLC. Usuario ({apodo}) pregunta: {mensaje}. Responde con ejemplos prácticos, ejercicios y consejos, sin gastar tokens innecesarios."
    elif servicio == "horoscopo":
        prompt = f"Eres un experto en horóscopos y bienestar natural. Usuario ({apodo}) pregunta: {mensaje}. Responde con horóscopo breve y consejos de bienestar."

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7,
            max_tokens=300
        )
        respuesta_texto = response.choices[0].message.content.strip()
        return {"respuesta": respuesta_texto}
    except Exception as e:
        return JSONResponse({"respuesta": f"Error al generar respuesta: {str(e)}"})
