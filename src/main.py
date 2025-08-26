import os, stripe, json
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

# Claves Stripe y código secreto desde variables de entorno
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
FREE_CODE = os.getenv("SECRET_FREE_CODE", "MKM991775")  # Código secreto opcional

stripe.api_key = STRIPE_SECRET_KEY

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Templates y static
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Cargar datos médicos y urgencias
with open("enfermedades.json", "r", encoding="utf-8") as f:
    medical_data = json.load(f)

with open("urgencias.json", "r", encoding="utf-8") as f:
    emergency_guide = json.load(f)

print("✅ Datos de enfermedades y urgencias cargados en memoria")

# Página principal
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Crear sesión de pago o verificar código secreto
@app.post("/pay/create-session")
async def create_session(
    apodo: str = Form(...),
    servicio: str = Form(...),
    codigo: str = Form(None)
):
    if not apodo:
        raise HTTPException(400, "Debes ingresar un apodo, sobrenombre o número.")
    
    # Verificación de código secreto para servicio gratis
    if codigo == FREE_CODE:
        return {"url": f"/consulta?apodo={apodo}&servicio={servicio}"}
    
    # Si no tiene código secreto, se requiere pago
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Médico Virtual May Roga - {servicio}"},
                    "unit_amount": 1500
                },
                "quantity": 1
            }],
            success_url=os.getenv("SUCCESS_URL", f"https://medico-virtual-may-roga.onrender.com/consulta?apodo={apodo}&servicio={servicio}"),
            cancel_url=os.getenv("CANCEL_URL", "https://medico-virtual-may-roga.onrender.com/cancel"),
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(400, str(e))

# Webhook Stripe
@app.post("/webhook-stripe")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(400, f"Webhook error: {e}")

    if event["type"] in ("checkout.session.completed", "payment_intent.succeeded"):
        print("✅ Pago confirmado, habilitar acceso de servicio.")

    return JSONResponse({"received": True})

# Consultas virtuales del Médico May Roga
@app.get("/consulta", response_class=HTMLResponse)
async def consulta(request: Request, apodo: str, servicio: str):
    # Aquí se puede integrar la IA para generar respuestas médicas
    return templates.TemplateResponse("consulta.html", {
        "request": request,
        "apodo": apodo,
        "servicio": servicio,
        "medical_data": medical_data,
        "emergency_guide": emergency_guide
    })

# Éxito y cancelación de pago
@app.get("/success", response_class=HTMLResponse)
async def success(request: Request):
    return HTMLResponse("<h1>✅ Pago exitoso. Acceso habilitado.</h1>")

@app.get("/cancel", response_class=HTMLResponse)
async def cancel(request: Request):
    return HTMLResponse("<h1>❌ Pago cancelado.</h1>")
