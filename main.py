import os
import json
import stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import httpx

# --- Variables de entorno ---
MAYROGA_ACCESS_CODE = os.getenv("MAYROGA_ACCESS_CODE")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

stripe.api_key = STRIPE_SECRET_KEY

app = FastAPI()

# --- CORS abierto para Google Sites ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Usuarios (para ejemplos de seguimiento) ---
USERS_FILE = "users.json"
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# --- Endpoint principal ---
@app.get("/")
async def home():
    return {"status": "ok", "message": "Asistente May Roga activo"}

# --- Crear sesión de pago Stripe ---
@app.post("/create-checkout-session")
async def create_checkout_session(req: Request):
    data = await req.json()
    product = data.get("product")
    amount = data.get("amount")
    if not product or not amount:
        raise HTTPException(status_code=400, detail="Producto o monto inválido")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": product},
                    "unit_amount": int(amount),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{req.headers.get('origin')}/success",
            cancel_url=f"{req.headers.get('origin')}/cancel",
        )
        return JSONResponse({"id": session.id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Validación de código secreto ---
def validate_secret(code: str):
    return code == MAYROGA_ACCESS_CODE

# --- Generador de eventos SSE ---
async def event_generator(service: str, secret: str):
    total_seconds = 10  # inicializado correctamente
    if secret == MAYROGA_ACCESS_CODE:
        access = "granted"
    else:
        access = "denied"
        yield json.dumps({"access": access}).encode()
        return

    yield json.dumps({"access": access, "service": service}).encode()

    # Simulación de envío de mensajes (voz o texto)
    messages = [f"Iniciando servicio: {service}", "Ejercicio 1", "Ejercicio 2", "Ejercicio 3"]
    for msg in messages:
        await asyncio.sleep(2)
        yield json.dumps({"message": msg}).encode()

# --- Endpoint SSE ---
@app.get("/assistant-stream")
async def assistant_stream(service: str, secret: str):
    async def streamer():
        async for event in event_generator(service, secret):
            yield b"data: " + event + b"\n\n"
    return StreamingResponse(streamer(), media_type="text/event-stream")

# --- Claves para frontend ---
@app.get("/config")
async def get_config():
    return {"stripe_key": STRIPE_PUBLISHABLE_KEY}

# --- Run OpenAI o Gemini (ejemplo) ---
async def call_openai(prompt: str):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.openai.com/v1/chat/completions", 
                                     headers=headers, json={"model":"gpt-4","messages":[{"role":"user","content":prompt}]})
        return response.json()

async def call_gemini(prompt: str):
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    async with httpx.AsyncClient() as client:
        response = await client.post("https://gemini.api.ai/some_endpoint", headers=headers, json={"prompt": prompt})
        return response.json()
