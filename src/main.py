# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
import stripe
import os
import openai

# Configuración
SECRET_CODE_NAME = "MKM991775"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
stripe.api_key = STRIPE_SECRET_KEY

# Inicialización
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)
openai.api_key = OPENAI_API_KEY

# Servicios disponibles
SERVICES = {
    "horoscopo": {"name": "Horóscopo", "duration": 35, "price": 3},
    "risoterapia": {"name": "Risoterapia y Bienestar", "duration": 10, "price": 12},
    "asistente": {"name": "Asistente Virtual Médico", "duration": 8, "price": 5}
}

@app.get("/", response_class=HTMLResponse)
async def index():
    template = env.get_template("index.html")
    return template.render(services=SERVICES, stripe_key=STRIPE_PUBLISHABLE_KEY)

@app.post("/access")
async def access_service(apodo: str = Form(...), code: str = Form("")):
    if code == SECRET_CODE_NAME:
        return JSONResponse({"status": "ok", "message": f"Acceso concedido para {apodo}. Ya puedes usar todos los servicios."})
    return JSONResponse({"status": "fail", "message": "Código secreto incorrecto."})

@app.post("/create-checkout-session")
async def create_checkout_session(apodo: str = Form(...), service: str = Form(...)):
    if service not in SERVICES:
        return JSONResponse({"error": "Servicio no válido"})
    product = SERVICES[service]
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': f"{product['name']} ({product['duration']} min)"},
                    'unit_amount': int(product['price'] * 100),
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=f"https://tu-dominio.com/success?apodo={apodo}&service={service}",
            cancel_url=f"https://tu-dominio.com/cancel",
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            # Aquí llamas al servicio: iniciar Asistente/Risoterapia/Horóscopo
            apodo = session["metadata"]["apodo"] if "metadata" in session else "Usuario"
            # Log o iniciar servicio real
            print(f"Acceso concedido vía pago para {apodo}")
        return JSONResponse({"status": "success"})
    except Exception as e:
        return JSONResponse({"status": "fail", "error": str(e)})

@app.post("/send-message")
async def send_message(apodo: str = Form(...), message: str = Form(...), service: str = Form(...)):
    # Llamada a OpenAI para respuesta inteligente
    if not message.strip():
        return JSONResponse({"response": "No se recibió mensaje."})
    prompt = f"Servicio: {service}\nApodo: {apodo}\nMensaje: {message}\nRespuesta:"
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )
        answer = response.choices[0].text.strip()
        return JSONResponse({"response": answer})
    except Exception as e:
        return JSONResponse({"response": f"Error generando respuesta: {str(e)}"})
