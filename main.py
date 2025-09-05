import os
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import stripe
import httpx
import json

# ----------------- CONFIG -----------------
RENDER_URL = "https://asistente-virtual-may-roga.onrender.com"
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
ACCESS_CODE = os.getenv("MAYROGA_ACCESS_CODE")  # código secreto directo desde Render

stripe.api_key = STRIPE_SECRET_KEY

# ----------------- APP -----------------
app = FastAPI()

# Permitir a Google Sites y cualquier origen conectarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- PLANTILLAS Y ESTÁTICOS -----------------
templates = Environment(loader=FileSystemLoader("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----------------- USUARIOS -----------------
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# ----------------- RUTAS -----------------
@app.get("/", response_class=HTMLResponse)
async def index():
    template = templates.get_template("index.html")
    return template.render(stripe_public_key=STRIPE_PUBLIC_KEY)

@app.post("/access")
async def access_service(code: str = Form(...)):
    if code != ACCESS_CODE:
        raise HTTPException(status_code=403, detail="Código incorrecto")
    return JSONResponse({"status": "ok", "message": "Acceso autorizado"})

@app.post("/create-payment-intent")
async def create_payment(amount: int = Form(...)):
    # Stripe requiere cantidad en centavos
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount * 100,
            currency="usd",
        )
        return JSONResponse({"client_secret": intent.client_secret})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ----------------- SERVICIO DE MENSAJES (TEXTO Y AUDIO) -----------------
@app.post("/assistant")
async def assistant(request: Request):
    data = await request.json()
    user_message = data.get("message")
    user_id = data.get("user_id")

    if not user_message or not user_id:
        raise HTTPException(status_code=400, detail="Datos incompletos")

    # Aquí se haría la llamada a OpenAI y Gemini
    async with httpx.AsyncClient() as client:
        # Ejemplo de llamada a OpenAI
        ai_response = f"Respuesta simulada para '{user_message}' usando OpenAI/Gemini"

    # Guardar historial usuario
    users = load_users()
    if user_id not in users:
        users[user_id] = []
    users[user_id].append({"user": user_message, "assistant": ai_response})
    save_users(users)

    return JSONResponse({"response": ai_response})

# ----------------- FIN -----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
