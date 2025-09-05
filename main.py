from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import stripe, time, asyncio, os, json
import openai  # Asegúrate de tener openai instalado y tu API key en variables de entorno
from langdetect import detect  # Para detección de idioma automática

# Configuración Stripe y OpenAI
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="Asistente May Roga 24/7")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Código secreto para administración
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "MI_CODIGO_SECRETO")

# Servicios y duración en minutos
SERVICIOS = {
    "Risoterapia y Bienestar Natural": 10,
    "Horóscopo": 2,
    "Respuesta Rápida": 0.9167  # 55 seg
}

# Clientes activos
clientes = {}

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
            success_url=f"{os.getenv('FRONTEND_URL')}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL')}/cancel",
        )
        return {"id": session.id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- GENERAR MENSAJES DEL ASISTENTE ---
async def generate_messages(service: str, prompt: str):
    """
    Conecta con OpenAI para generar mensajes dinámicos de los servicios.
    Aplica técnicas TVid y dualidad positiva/negativa.
    """
    if not prompt:
        prompt = f"Usuario inicia servicio {service}. Genera mensajes paso a paso, amables, profesionales, respetuosos, integrando dualidad y TVid, sin contacto físico."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Actúa como Asistente May Roga, voz amable, respetuosa, profesional, usando técnicas TVid, dualidad positiva/negativa, 24/7."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        texto = response.choices[0].message.content.strip()
        # Dividir en mensajes por saltos de línea
        mensajes = [msg for msg in texto.split("\n") if msg.strip()]
        return mensajes
    except Exception as e:
        return [f"Error generando mensajes: {str(e)}"]

# --- ENDPOINT SSE: ASISTENTE STREAM ---
@app.get("/assistant-stream")
async def assistant_stream(request: Request, service: str, prompt: str = "", secret: str = None):
    if secret and secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Código secreto incorrecto")
    if service not in SERVICIOS:
        raise HTTPException(status_code=400, detail="Servicio no encontrado")

    duration_minutes = SERVICIOS[service]
    total_seconds = int(duration_minutes * 60)
    mensajes = await generate_messages(service, prompt)

    async def event_generator():
        start_time = time.time()
        msg_index = 0
        while total_seconds > 0:
            if await request.is_disconnected():
                break
            # Enviar mensaje cada intervalo
            if msg_index < len(mensajes):
                yield f"data: {mensajes[msg_index]}\n\n"
                msg_index += 1
            await asyncio.sleep(total_seconds / max(len(mensajes),1))
            total_seconds -= total_seconds / max(len(mensajes),1)
        yield f"data: Sesión de {service} finalizada ✅\n\n"

    # Guardar cliente activo
    clientes[request.client.host] = {"service": service, "start": time.time(), "duration": duration_minutes}

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- ENDPOINTS SUCCESS / CANCEL ---
@app.get("/success")
async def success(session_id: str):
    return {"message": f"Pago completado! ID de sesión: {session_id}"}

@app.get("/cancel")
async def cancel():
    return {"message": "Pago cancelado."}

# --- ENDPOINT ADMIN PARA VER CLIENTES ACTIVOS ---
@app.get("/admin/clients")
async def admin_clients(secret: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Código secreto incorrecto")
    return {"clientes_activos": clientes}
