import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import stripe
import openai
from dotenv import load_dotenv

load_dotenv()

# Configuraciones
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
SECRET_CODE = os.getenv("SECRET_CODE")  # Código secreto para acceso gratis

openai.api_key = OPENAI_API_KEY
stripe.api_key = STRIPE_SECRET_KEY

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Servicios y precios
SERVICIOS = {
    "medico": {"nombre": "Asistente Virtual Médico", "precio": 5.0, "duracion": "8 min"},
    "risoterapia": {"nombre": "Risoterapia y Bienestar Natural", "precio": 12.0, "duracion": "10 min"},
    "horoscopo": {"nombre": "Horóscopo", "precio": 3.0, "duracion": "1:30 min"}
}

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stripe_pub_key": STRIPE_PUBLISHABLE_KEY,
        "servicios": SERVICIOS
    })

@app.post("/chat")
async def chat(
    apodo: str = Form(...),
    mensaje: str = Form(...),
    servicio: str = Form(...),
    codigo: str = Form(default=None),
    pago_confirmado: str = Form(default="false")
):
    # Validación de acceso
    acceso_gratis = codigo == SECRET_CODE and apodo
    acceso_pago = pago_confirmado == "true" and apodo
    if not (acceso_gratis or acceso_pago):
        return JSONResponse({"respuesta": "Acceso denegado. Verifica apodo, código secreto o pago."})

    # Construir prompt según servicio
    prompt = ""
    if servicio == "medico":
        prompt = f"Eres un médico profesional. Responde al usuario '{apodo}' sobre: {mensaje}. Atención: modo informativo, no sustituye consulta presencial."
    elif servicio == "risoterapia":
        prompt = f"Eres un especialista en risoterapia y bienestar natural usando Técnicas de Vida (Tvid). Responde al usuario '{apodo}' sobre: {mensaje}. Incluye ejercicios prácticos y dualidad positivo/negativo."
    elif servicio == "horoscopo":
        prompt = f"Eres un horoscopo experto. Responde al usuario '{apodo}' sobre: {mensaje}. Duración de la respuesta: breve, 1-2 frases."
    else:
        prompt = f"Responde al usuario '{apodo}': {mensaje}"

    # Llamada a OpenAI Chat Completions
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Error al generar respuesta: {str(e)}"

    return JSONResponse({"respuesta": answer})

@app.post("/create-checkout-session")
async def create_checkout_session(servicio: str = Form(...), apodo: str = Form(...)):
    if servicio not in SERVICIOS:
        return JSONResponse({"error": "Servicio no válido"}, status_code=400)
    item = SERVICIOS[servicio]
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item['nombre']},
                    'unit_amount': int(item['precio'] * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"https://tu-web.com?apodo={apodo}&servicio={servicio}&pago=true",
            cancel_url="https://tu-web.com",
        )
        return JSONResponse({"id": session.id})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
