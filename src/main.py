# src/main.py
import os
import json
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import stripe
import openai

# ----- CONFIG (usar variables de entorno en Render) -----
# STRIPE_SECRET_KEY            -> clave privada de Stripe
# STRIPE_WEBHOOK_SECRET        -> secreto del webhook de Stripe
# FRONTEND_URL                 -> URL pública de tu web (ej: https://medico-virtual-may-roga.onrender.com)
# OPENAI_API_KEY               -> clave OpenAI (si la tienes)
# SECRET_CODE_NAME             -> código secreto (si quieres cambiarlo, por defecto MKM991775)

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:10000")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SECRET_CODE_NAME = os.environ.get("SECRET_CODE_NAME", "MKM991775")

# Inicializar librerías
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

app = FastAPI()

# Montar static solo si existe (evita errores si no la creaste)
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# ----- Servicios y precios (en USD) -----
SERVICES = {
    "asistente_virtual": {"label": "Asistente Virtual Médico", "price_cents": 500, "time_min": 8},
    "risoterapia": {"label": "Risoterapia y Bienestar", "price_cents": 1200, "time_min": 10},
    "horoscopo": {"label": "Horóscopo", "price_cents": 300, "time_min": 1},  # 35s ~ 1min
}

# Memoria en RAM para usuarios activos (apodo -> active True/False)
# Nota: por simplicidad es in-memory. Si reinicias el servicio se pierde.
ACTIVE_USERS: dict = {}

# Carga de backups offline opcional
def load_json_safe(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

BACKUP_BEHAVIOR = load_json_safe("behavior_guide.json")
BACKUP_ENFERMEDADES = load_json_safe("enfermedades.json")
BACKUP_URGENCIAS = load_json_safe("urgencias.json")

# ---------- RUTAS ----------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Renderiza la página principal. Pasa la lista de servicios para llenar el select dinámicamente.
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "services": {
                key: {"name": v["label"], "time": f"{v['time_min']} min", "price": v["price_cents"] // 100}
                for key, v in SERVICES.items()
            },
            "frontend_url": FRONTEND_URL
        }
    )

@app.post("/access-secret")
async def access_secret(apodo: str = Form(...), code: str = Form(...)):
    """
    Acceso directo con código secreto. Activa el apodo.
    """
    if not apodo:
        return JSONResponse({"success": False, "message": "Apodo requerido."}, status_code=400)

    if code.strip().upper() == SECRET_CODE_NAME.upper():
        ACTIVE_USERS[apodo] = {"active": True, "via": "secret"}
        return JSONResponse({"success": True, "message": f"Acceso concedido para {apodo}."})
    return JSONResponse({"success": False, "message": "Código secreto incorrecto."}, status_code=403)

@app.post("/create-checkout-session")
async def create_checkout_session(apodo: str = Form(...), servicio: str = Form(...)):
    """
    Crea sesión de Checkout en Stripe. REDIRIGE al cliente a Stripe.
    success_url incluirá apodo y servicio para que frontend lo muestre.
    """
    if not STRIPE_SECRET_KEY:
        return JSONResponse({"error": "Stripe no configurado en el servidor."}, status_code=500)

    if servicio not in SERVICES:
        return JSONResponse({"error": "Servicio inválido."}, status_code=400)

    try:
        prod = SERVICES[servicio]
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": prod["label"]},
                    "unit_amount": prod["price_cents"],
                },
                "quantity": 1,
            }],
            mode="payment",
            metadata={"apodo": apodo, "servicio": servicio},
            success_url=f"{FRONTEND_URL}/?apodo={apodo}&servicio={servicio}",
            cancel_url=f"{FRONTEND_URL}",
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Webhook que Stripe llama cuando el pago se completa.
    Marca al apodo como activo para dar servicio.
    """
    if not STRIPE_WEBHOOK_SECRET:
        return JSONResponse({"error": "Webhook secret no configurado."}, status_code=500)

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Firma Stripe no válida")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Evento de checkout completado
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        apodo = session.get("metadata", {}).get("apodo")
        servicio = session.get("metadata", {}).get("servicio")
        if apodo:
            ACTIVE_USERS[apodo] = {"active": True, "via": "stripe", "servicio": servicio}
            # Aquí puedes registrar en DB / enviar correo / guardar logs
            print(f"[WEBHOOK] Pago confirmado: apodo={apodo} servicio={servicio}")

    return JSONResponse({"received": True})

@app.post("/chat")
async def chat(apodo: str = Form(...), message: str = Form(...), servicio: Optional[str] = Form(None)):
    """
    Endpoint que responde usando OpenAI si está disponible; si no, usa respuestas de backup.
    Requiere apodo activo (por código secreto o por pago webhooks).
    """
    if not apodo or not message:
        return JSONResponse({"error": "apodo y message son requeridos"}, status_code=400)

    user = ACTIVE_USERS.get(apodo)
    if not user or not user.get("active"):
        return JSONResponse({"error": "Acceso denegado. Paga o usa código secreto."}, status_code=403)

    # System prompt breve y responsable (informativo, no sustituto de profesional)
    system_prompt = (
        "Eres 'Asistente Virtual Médico' informativo, basado en May Roga LLC. "
        "Tus respuestas deben ser claras, cortas, no alarmistas. Indica siempre que la información es orientativa "
        "y recomienda consulta presencial cuando haya signos de alarma. No ordenar recetas legales peligrosas."
    )

    # Ajusta el comportamiento según servicio
    if servicio is None:
        servicio = ACTIVE_USERS.get(apodo, {}).get("servicio", "asistente_virtual")

    # Construir prompt final
    user_prompt = f"Servicio: {servicio}\nApodo: {apodo}\nConsulta: {message}\n\nResponde brevemente (máx 150 palabras)."

    # Intentar OpenAI
    if OPENAI_API_KEY:
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=400,
            )
            text = resp.choices[0].message.content.strip()
            return JSONResponse({"respuesta": text})
        except Exception as e:
            # log y fallback
            print("OpenAI error:", str(e))

    # FALLBACK OFFLINE: usar backups si existen, o respuesta genérica
    # Intentamos buscar coincidencias simples en archivos de respaldo
    text_fallback = None
    q = message.lower()
    # ejemplo simple: si encuentra 'fiebre' en enfermedades
    for _, data in (("enf", BACKUP_ENFERMEDADES), ("urg", BACKUP_URGENCIAS)):
        try:
            # BACKUP_ENFERMEDADES esperado: {"fiebre": "...", ...}
            for k, v in data.items():
                if k.lower() in q:
                    text_fallback = v if isinstance(v, str) else json.dumps(v)
                    break
            if text_fallback:
                break
        except Exception:
            continue

    if not text_fallback:
        text_fallback = (f"Respuesta generada para '{apodo}': recibí '{message}'. "
                         "Esto es informativo. Si hay urgencia, busca atención médica presencial.")

    return JSONResponse({"respuesta": text_fallback})

# Health check
@app.get("/ping")
async def ping():
    return {"status": "ok"}
