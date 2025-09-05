import os
import json
import stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# --- Variables de entorno de Render ---
RENDER_URL = "https://asistente-virtual-may-roga.onrender.com"
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
ACCESS_CODE = os.getenv("MAYROGA_ACCESS_CODE")  # Tu código secreto desde Render

# --- Inicialización Stripe ---
stripe.api_key = STRIPE_SECRET_KEY

# --- FastAPI ---
app = FastAPI()

# --- CORS para Google Sites y cualquier web ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir acceso desde cualquier web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static files y templates ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Usuarios (para servicios bloqueados, si fuera necesario) ---
USERS_FILE = "users.json"
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# --- Ruta principal ---
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "stripe_key": STRIPE_PUBLIC_KEY})

# --- Crear sesión de pago Stripe ---
@app.post("/create-checkout-session")
async def create_checkout_session(data: dict):
    product = data.get("product")
    amount = data.get("amount")
    if not product or not amount:
        raise HTTPException(status_code=400, detail="Producto o monto no definido")

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
            success_url=f"{RENDER_URL}/success",
            cancel_url=f"{RENDER_URL}/cancel",
        )
        return JSONResponse({"id": session.id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Acceso a servicios con código secreto ---
@app.get("/assistant-stream")
async def assistant_stream(service: str, secret: str):
    if secret != ACCESS_CODE:
        return JSONResponse({"access": "denied"}, status_code=403)

    return JSONResponse({"access": "granted", "service": service})

# --- Reproducción de audios de Tvid (opcional, si quieres rutas directas) ---
@app.get("/audio/{tvid_name}")
async def get_audio(tvid_name: str):
    audio_path = f"static/audio/{tvid_name}.mp3"
    if os.path.exists(audio_path):
        return JSONResponse({"audio_path": f"/static/audio/{tvid_name}.mp3"})
    else:
        raise HTTPException(status_code=404, detail="Audio no encontrado")
