# src/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
import stripe
import os

# ===== CONFIGURACIONES =====
SECRET_CODE_NAME = "MKM991775"
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Tu clave secreta de Stripe

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# ===== SIMULACIÓN DE SERVICIOS =====
SERVICIOS = {
    "asistente_virtual": "Asistente Virtual Médico activado, duración 8 min.",
    "risoterapia": "Sesión de Risoterapia y Bienestar Natural activada, duración 10 min.",
    "horoscopo": "Consulta de Horóscopo activada, duración 35 seg."
}

# ===== INICIO SERVICIO CON CÓDIGO SECRETO =====
@app.post("/start-service-secret")
async def start_service_secret(request: Request):
    form = await request.form()
    apodo = form.get("apodo")
    codigo = form.get("codigo", "").upper()

    if not apodo or not codigo:
        return JSONResponse({"error": "Apodo y código son obligatorios"}, status_code=400)

    if codigo != SECRET_CODE_NAME.upper():
        return JSONResponse({"error": "Código secreto incorrecto"}, status_code=403)

    # Retorna los servicios disponibles
    return JSONResponse({"resultado": f"Hola {apodo}, acceso concedido. Selecciona tu servicio para comenzar."})

# ===== CREAR SESIÓN DE PAGO STRIPE =====
@app.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    form = await request.form()
    apodo = form.get("apodo")
    servicio = form.get("servicio")

    if not apodo or not servicio:
        return JSONResponse({"error": "Apodo y servicio son obligatorios"}, status_code=400)

    if servicio not in SERVICIOS:
        return JSONResponse({"error": "Servicio no válido"}, status_code=400)

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": SERVICIOS[servicio]},
                    "unit_amount": 500 if servicio=="asistente_virtual" else 1200 if servicio=="risoterapia" else 300
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"{os.getenv('SUCCESS_URL')}?apodo={apodo}&servicio={servicio}",
            cancel_url=os.getenv('CANCEL_URL')
        )
        return JSONResponse({"url": checkout_session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ===== WEBHOOK STRIPE =====
@app.post("/webhook-stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    # Solo confirma que el pago fue exitoso
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        apodo = session.get("client_reference_id", "Usuario")
        servicio = session.get("metadata", {}).get("servicio", "asistente_virtual")
        # Aquí se podría marcar en DB que el servicio está activo
        print(f"Pago exitoso: {apodo} activó {servicio}")
    return JSONResponse({"status": "ok"})

# ===== OBTENER SERVICIO =====
@app.post("/get-service")
async def get_service(request: Request):
    form = await request.form()
    apodo = form.get("apodo")
    servicio = form.get("servicio")

    if not apodo or not servicio:
        return JSONResponse({"error": "Apodo y servicio son obligatorios"}, status_code=400)

    resultado = SERVICIOS.get(servicio, "Servicio no disponible")
    return JSONResponse({"resultado": resultado})

# ===== CHAT CON ASISTENTE =====
@app.post("/chat")
async def chat(request: Request):
    form = await request.form()
    apodo = form.get("apodo")
    message = form.get("message")

    if not apodo or not message:
        return JSONResponse({"error": "Apodo y mensaje son obligatorios"}, status_code=400)

    # Respuesta simulada (aquí puedes integrar IA)
    respuesta = f"{apodo}, tu mensaje '{message}' ha sido recibido por Asistente Virtual Médico."
    return JSONResponse({"respuesta": respuesta})

# ===== RUTA RAÍZ =====
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
