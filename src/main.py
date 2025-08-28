import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import stripe
import openai

# Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
FREE_ACCESS_CODE = os.getenv("FREE_ACCESS_CODE")  # tu código secreto

stripe.api_key = STRIPE_SECRET_KEY
openai.api_key = OPENAI_API_KEY

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

SERVICES = {
    "medico": {"name": "Asistente Virtual Médico", "price": 500, "duration": 8},
    "risoterapia": {"name": "Risoterapia y Bienestar Natural", "price": 1200, "duration": 10},
    "horoscopo": {"name": "Horóscopo", "price": 300, "duration": 1.5},
}

paid_users = set()
free_access_users = set()

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "services": SERVICES})

@app.post("/chat")
async def chat(
    apodo: str = Form(...),
    servicio: str = Form(...),
    mensaje: str = Form(...),
):
    if apodo not in paid_users and apodo not in free_access_users:
        return JSONResponse({"respuesta": "Acceso denegado. Realiza el pago o ingresa código secreto."})
    
    system_msg = f"Eres un asistente de {SERVICES[servicio]['name']} de May Roga LLC."
    
    if servicio == "medico":
        prompt = f"Como médico informativo, responde de manera profesional al paciente: {mensaje}"
    elif servicio == "risoterapia":
        prompt = f"Como experto en risoterapia y bienestar natural según Técnicas de Vida, responde con ejercicios y ejemplos prácticos: {mensaje}"
    else:
        prompt = f"Como horóscopo, responde según signo y fecha de nacimiento: {mensaje}"

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
    )

    reply = response.choices[0].message.content
    return JSONResponse({"respuesta": reply})

@app.post("/acceso-gratis")
async def acceso_gratis(apodo: str = Form(...), code: str = Form(...)):
    if code == FREE_ACCESS_CODE:
        free_access_users.add(apodo)
        return JSONResponse({"status": "ok", "mensaje": f"Acceso concedido para {apodo} (gratis)."})
    return JSONResponse({"status": "error", "mensaje": "Código incorrecto."})

@app.post("/create-payment-intent")
async def create_payment_intent(servicio: str = Form(...), apodo: str = Form(...)):
    service = SERVICES.get(servicio)
    if not service:
        return JSONResponse({"error": "Servicio inválido"})
    intent = stripe.PaymentIntent.create(
        amount=service["price"],
        currency="usd",
        metadata={"apodo": apodo, "servicio": servicio},
    )
    return JSONResponse({"client_secret": intent.client_secret})

@app.post("/confirm-payment")
async def confirm_payment(apodo: str = Form(...)):
    paid_users.add(apodo)
    return JSONResponse({"status": "ok", "mensaje": f"Pago confirmado para {apodo}"})
