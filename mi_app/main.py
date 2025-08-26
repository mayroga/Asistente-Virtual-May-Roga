import os
import json
import stripe
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

# ------------------ CONFIGURACIONES ------------------
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
stripe.api_key = STRIPE_SECRET_KEY

# Crear app FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Templates y static
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ------------------ CARGA DE DATOS ------------------
with open("enfermedades.json", "r", encoding="utf-8") as f:
    enfermedades = json.load(f)

with open("urgencias.json", "r", encoding="utf-8") as f:
    urgencias = json.load(f)

print("✅ Datos de enfermedades y urgencias cargados en memoria")
print("✅ Datos enfer/urgencias cargados:", bool(enfermedades), bool(urgencias))

# Código secreto para servicio gratuito
SECRET_FREE_CODE = "MKM991775"

# ------------------ RUTAS ------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/medico-virtual")
async def medico_virtual(
    request: Request,
    apodo: str = Form(...),
    servicio: str = Form(...),
    pago_confirmado: str = Form(None),
    codigo: str = Form(None)
):
    if not apodo.strip():
        return JSONResponse({"error": "Debes indicar un apodo o sobrenombre."}, status_code=400)

    servicio_gratis = codigo == SECRET_FREE_CODE
    pago_valido = pago_confirmado == "ok" or servicio_gratis

    if not pago_valido:
        return JSONResponse({"error": "Servicio no habilitado. Debes pagar o usar el código secreto."}, status_code=403)

    resultado = {
        "mensaje": f"✅ Servicio habilitado para {apodo}.",
        "servicio": servicio,
        "informacion": {}
    }

    if servicio in enfermedades:
        resultado["informacion"] = enfermedades[servicio]
    elif servicio in urgencias:
        resultado["informacion"] = urgencias[servicio]
    else:
        resultado["informacion"] = {"nota": "Servicio seleccionado no encontrado. Proporcionar información general."}

    return JSONResponse(resultado)

# ------------------ CREAR SESIÓN DE PAGO ------------------
@app.post("/pay/create-session")
def create_session(servicio: str = Form(...), apodo: str = Form(...)):
    if not apodo.strip():
        raise HTTPException(400, "Debes indicar un apodo o sobrenombre.")

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
            success_url=os.getenv("SUCCESS_URL", "https://medico-virtual-may-roga.onrender.com/success"),
            cancel_url=os.getenv("CANCEL_URL", "https://medico-virtual-may-roga.onrender.com/cancel"),
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(400, str(e))

# ------------------ WEBHOOK STRIPE ------------------
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

# ------------------ RUTAS DE ÉXITO Y CANCELACIÓN ------------------
@app.get("/success", response_class=HTMLResponse)
async def success(request: Request):
    return HTMLResponse("<h1>✅ Pago exitoso. Acceso habilitado.</h1>")

@app.get("/cancel", response_class=HTMLResponse)
async def cancel(request: Request):
    return HTMLResponse("<h1>❌ Pago cancelado.</h1>")

# ------------------ API QUICK RESPONSE ------------------
@app.post("/api/message", response_model=None)
async def api_message(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    return {"ok": True, "data": data}
