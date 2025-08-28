from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import openai
import stripe

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuración de OpenAI y Stripe
openai.api_key = os.getenv("OPENAI_API_KEY")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Código secreto para acceso gratuito
FREE_CODE = os.getenv("FREE_CODE", "MKM991775")

# Servicios disponibles
SERVICES = {
    "agente_rapido": {"name": "Agente de Respuesta Rápida", "price": 1, "duration": 55},
    "risoterapia": {"name": "Risoterapia y Bienestar Natural", "price": 12, "duration": 600},
    "horoscopo": {"name": "Horóscopo", "price": 3, "duration": 90},
}

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "services": SERVICES})

@app.post("/chat")
async def chat(
    apodo: str = Form(...),
    service: str = Form(...),
    message: str = Form(...),
    pago_confirmado: str = Form(None),
    code: str = Form(None)
):
    # Verificar acceso
    acceso = False
    if code == FREE_CODE or pago_confirmado == "true":
        acceso = True

    if not acceso:
        return JSONResponse({"response": "Acceso denegado. Paga o usa el código secreto."})

    # Mensaje base según servicio
    system_prompt = ""
    if service == "agente_rapido":
        system_prompt = ("Eres un Agente de Respuesta Rápida. Responde de manera educativa sobre salud, bienestar, "
                         "risoterapia o horóscopo, sin dar diagnósticos ni tratamientos, máximo 55 segundos.")
    elif service == "risoterapia":
        system_prompt = ("Eres un experto en Risoterapia y Bienestar Natural basado en Técnicas de Vida. "
                         "Genera consejos prácticos, ejercicios y ejemplos positivos y negativos, duración 10 minutos.")
    elif service == "horoscopo":
        system_prompt = ("Eres un astrólogo que da horóscopos breves y claros, duración 1 minuto 30 segundos, "
                         "informativo y educativo.")
    else:
        system_prompt = "Respuesta educativa y segura."

    # Llamada a OpenAI
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"(Error generando respuesta): {e}"

    return JSONResponse({"response": answer})
