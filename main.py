from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import stripe, time, asyncio, json, os

# Configuración de Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Tu llave secreta de Stripe

app = FastAPI(title="Asistente May Roga 24/7")

# CORS para permitir conexión desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar a tu dominio en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Código secreto para administración
ADMIN_SECRET = "MI_CODIGO_SECRETO"

# Servicios y duración en minutos
SERVICIOS = {
    "Risoterapia y Bienestar Natural": 10,
    "Horóscopo": 2,
    "Respuesta Rápida": 0.9167  # 55 seg en minutos
}

# --- ENDPOINT: CREAR SESIÓN STRIPE ---
@app.post("/create-checkout-session")
async def create_checkout(data: dict):
    product = data.get("product")
    amount = data.get("amount")  # en centavos

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

# --- FUNCION SIMULADA DE ASISTENTE 24/7 ---
async def generate_messages(service: str):
    # Aquí se conectaría OpenAI/Geminis
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

# --- ENDPOINT SSE: ASISTENTE STREAM ---
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
        start_time = time.time()
        msg_index = 0

        while total_seconds > 0:
            if await request.is_disconnected():
                break
            # Enviar mensaje cada cierto tiempo (simulado)
            if msg_index < len(messages):
                yield f"data: {messages[msg_index]}\n\n"
                msg_index += 1
            await asyncio.sleep(total_seconds / max(len(messages),1))  # repartir mensajes
            total_seconds -= total_seconds / max(len(messages),1)
        yield f"data: Sesión de {service} finalizada ✅\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- ENDPOINTS SUCCESS / CANCEL (Opcional) ---
@app.get("/success")
async def success(session_id: str):
    return {"message": f"Pago completado! ID de sesión: {session_id}"}

@app.get("/cancel")
async def cancel():
    return {"message": "Pago cancelado."}
