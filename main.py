from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import stripe, time, asyncio, os

# --- Configuración Stripe ---
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Tu llave secreta de Stripe
STRIPE_PUBLISHABLE_KEY = "pk_live_51NqPxQBOA5mT4t0PEoRVRc0Sj7DugiHvxhozC3BYh0q0hAx1N3HCLJe4xEp3MSuNMA6mQ7fAO4mvtppqLodrtqEn00pgJNQaxz"

# --- FastAPI app ---
app = FastAPI(title="Asistente May Roga 24/7")
templates = Jinja2Templates(directory="templates")  # <-- templates en /templates

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar al dominio real en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Código secreto ---
ADMIN_SECRET = "MI_CODIGO_SECRETO"

# --- Servicios y duración en minutos ---
SERVICIOS = {
    "Risoterapia y Bienestar Natural": 10,
    "Horóscopo": 2,
    "Respuesta Rápida": 0.9167
}

# --- ENDPOINTS HTML ---
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "stripe_key": STRIPE_PUBLISHABLE_KEY})

@app.get("/success", response_class=HTMLResponse)
async def read_success(request: Request, session_id: str):
    return templates.TemplateResponse("success.html", {"request": request, "session_id": session_id})

# --- ENDPOINT: CREAR SESIÓN STRIPE ---
@app.post("/create-checkout-session")
async def create_checkout(data: dict):
    product = data.get("product")
    amount = data.get("amount")
    if not product or not amount:
        raise HTTPException(status_code=400, detail="Producto o monto faltante")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": product},
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"https://asistente-virtual-may-roga.onrender.com/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"https://asistente-virtual-may-roga.onrender.com/cancel",
        )
        return {"id": session.id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- ENDPOINT SSE: ASISTENTE STREAM ---
async def generate_messages(service: str):
    mensajes = []
    if service == "Risoterapia y Bienestar Natural":
        mensajes = [
            "¡Hola! Bienvenido a tu sesión de Risoterapia y Bienestar Natural 😊",
            "Vamos a realizar ejercicios TVid para mejorar tu energía y bienestar.",
            "Recuerda mantener una respiración profunda y relajada.",
            "Finalizando sesión, ¡gracias por participar!"
        ]
    elif service == "Horóscopo":
        mensajes = [
            "¡Hola! Revisemos tu horóscopo del día 🌟",
            "Hoy es un buen día para reflexionar y tomar decisiones importantes.",
            "Ejercicio TVid: escribe tres cosas positivas que sucedieron hoy.",
            "Sesión de horóscopo finalizada ✅"
        ]
    elif service == "Respuesta Rápida":
        mensajes = [
            "¡Hola! Respuesta rápida activada ⚡",
            "Pregunta sobre salud, educación, ejercicios, risoterapia, horóscopo o consejos.",
            "Finalizando respuesta rápida, ¡gracias por usar el servicio!"
        ]
    return mensajes

@app.get("/assistant-stream")
async def assistant_stream(request: Request, service: str, secret: str = None):
    if secret and secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Código secreto incorrecto")
    if service not in SERVICIOS:
        raise HTTPException(status_code=400, detail="Servicio no encontrado")
    duration_minutes = SERVICIOS[service]
    total_seconds = int(duration_minutes * 60)

    async def event_generator():
        messages = await generate_messages(service)
        msg_index = 0
        while total_seconds > 0:
            if await request.is_disconnected():
                break
            if msg_index < len(messages):
                yield f"data: {messages[msg_index]}\n\n"
                msg_index += 1
            await asyncio.sleep(total_seconds / max(len(messages), 1))
            total_seconds -= total_seconds / max(len(messages), 1)
        yield f"data: Sesión de {service} finalizada ✅\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- ENDPOINT: OBTENER PRODUCTO DE SESIÓN ---
@app.get("/get-session")
async def get_session(session_id: str):
    try:
        # Expandir line_items para obtener producto
        session = stripe.checkout.Session.retrieve(session_id, expand=["line_items"])
        line_items = session.line_items
        product_name = line_items.data[0].description if line_items.data else "Producto desconocido"

        # Mapear nombre de producto a servicio interno
        if "Risoterapia" in product_name:
            service = "Risoterapia y Bienestar Natural"
        elif "Horóscopo" in product_name:
            service = "Horóscopo"
        elif "Respuesta Rápida" in product_name:
            service = "Respuesta Rápida"
        else:
            service = "Desconocido"

        return {"product": service}

    except Exception as e:
        return {"error": str(e)}
