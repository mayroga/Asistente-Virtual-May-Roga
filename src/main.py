import os
import stripe
import openai
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Claves
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY
CODE_SECRET = os.getenv("CODE_SECRET")  # tu código secreto

# Servicios
SERVICIOS = {
    "medico": {"precio": 5.0, "duracion": 8},
    "risoterapia": {"precio": 12.0, "duracion": 10},
    "horoscopo": {"precio": 3.0, "duracion": 1.5},
}

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "servicios": SERVICIOS})

@app.post("/chat")
async def chat(
    apodo: str = Form(...),
    mensaje: str = Form(...),
    servicio: str = Form(...),
    pago_confirmado: str = Form(...),
    codigo: str = Form(None)
):
    acceso_gratis = codigo == CODE_SECRET
    acceso_pago = pago_confirmado == "true"

    if not (acceso_gratis or acceso_pago):
        return JSONResponse({"respuesta": "Acceso denegado. Debes pagar o usar un código secreto."})

    prompt = ""
    if servicio == "medico":
        prompt = f"(ASISTENTE MÉDICO) Responde profesionalmente al paciente '{apodo}': {mensaje}"
    elif servicio == "risoterapia":
        prompt = f"(RISOTERAPIA) Basado en las Técnicas de Vida de May Roga LLC, responde al participante '{apodo}': {mensaje}"
    elif servicio == "horoscopo":
        prompt = f"(HORÓSCOPO) Genera un horóscopo profesional breve para '{apodo}': {mensaje}"
    else:
        prompt = f"Responde profesionalmente a '{apodo}': {mensaje}"

    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        respuesta_texto = response.choices[0].message.content.strip()
    except Exception as e:
        respuesta_texto = f"Error al generar respuesta: {str(e)}"

    return JSONResponse({"respuesta": respuesta_texto})
