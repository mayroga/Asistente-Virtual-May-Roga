import os, json, stripe, secrets, time
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, Body, Query, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

# =========================
# Configuración y Stripe
# =========================
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
BASE_URL = os.getenv("BASE_URL", "https://medico-virtual-may-roga.onrender.com")
FREE_PASS_CODE = os.getenv("FREE_PASS_CODE", "MKM991775")
stripe.api_key = STRIPE_SECRET_KEY

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# =========================
# Memoria en servidor
# =========================
ACTIVE_TOKENS: Dict[str, Dict[str, Any]] = {}
PAID_NICKNAMES = set()

# =========================
# Carga de datos locales (corregido ruta a raíz)
# =========================
try:
    with open(os.path.join(BASE_DIR, "../enfermedades.json"), "r", encoding="utf-8") as f:
        ENF = json.load(f)
    with open(os.path.join(BASE_DIR, "../urgencias.json"), "r", encoding="utf-8") as f:
        URG = json.load(f)
    print("✅ Datos de enfermedades y urgencias cargados en memoria")
except Exception as e:
    print("⚠️ No se pudieron cargar los datos locales:", e)
    ENF, URG = [], {}

ENF_IDX = {e["nombre"].lower(): e for e in ENF}

# =========================
# Página raíz
# =========================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, paid: str | None = None, nickname: str | None = None):
    return templates.TemplateResponse("index.html", {"request": request, "paid": paid, "nickname": nickname})

# =========================
# Sesión y Acceso
# =========================
@app.post("/api/start-session")
async def start_session(payload: Dict[str, Any] = Body(...)):
    nickname = (payload.get("nickname") or "").strip()
    code = (payload.get("code") or "").strip()
    if not nickname:
        raise HTTPException(400, "Apodo obligatorio.")

    if code and secrets.compare_digest(code, FREE_PASS_CODE):
        token = secrets.token_urlsafe(32)
        ACTIVE_TOKENS[token] = {"nickname": nickname, "created": time.time(), "paid": True, "free": True}
        return {"ok": True, "token": token, "access": "free"}

    if nickname in PAID_NICKNAMES:
        token = secrets.token_urlsafe(32)
        ACTIVE_TOKENS[token] = {"nickname": nickname, "created": time.time(), "paid": True, "free": False}
        return {"ok": True, "token": token, "access": "paid"}

    return {"ok": True, "requires_payment": True}

@app.get("/api/check-access")
async def check_access(nickname: str = Query(...)):
    return {"paid": nickname in PAID_NICKNAMES}

# =========================
# Stripe: crear checkout
# =========================
@app.post("/pay/create-session")
def create_session(nickname: str = Query(...)):
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            client_reference_id=nickname,
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Médico Virtual May Roga - Sesión"},
                    "unit_amount": int(os.getenv("PRICE_USD_CENTS", "1500"))
                },
                "quantity": 1
            }],
            success_url=f"{BASE_URL}?paid=1&nickname={nickname}",
            cancel_url=f"{BASE_URL}?paid=0&nickname={nickname}",
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(400, str(e))

# =========================
# Webhook Stripe
# =========================
@app.post("/webhook-stripe")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(400, f"Webhook error: {e}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        nickname = session.get("client_reference_id")
        if nickname:
            PAID_NICKNAMES.add(nickname)
            print(f"✅ Pago confirmado para '{nickname}'. Acceso habilitado.")
    return JSONResponse({"received": True})

# =========================
# Chat híbrido: offline + OpenAI/Gemini
# =========================
SAFETY_FOOTER = (
    "\n\n—\nInformación educativa. No es diagnóstico médico personal ni indica dosis. "
    "Si hay síntomas graves o empeoran: acudir a urgencias o contactar a un profesional presencial."
)

EMERGENCY_SIGNS = ["dolor torácico", "ahogo", "disnea severa", "debilidad en un lado", "convulsión",
                   "sangrado abundante", "fiebre muy alta", "pérdida de conciencia", "envenenamiento", "trauma severo"]

def quick_triage(text: str) -> str | None:
    t = text.lower()
    for s in EMERGENCY_SIGNS:
        if s in t:
            return ("⚠️ Posibles signos de urgencia: "
                    f"\"{s}\". Si es actual, llama a emergencias de tu zona o acude a un servicio de urgencias. "
                    "No demores la atención.")
    return None

def match_condition(text: str) -> Dict[str, Any] | None:
    t = text.lower()
    for name, data in ENF_IDX.items():
        if any(word in t for word in name.split()):
            return data
    keywords = {
        "tos": "Neumonía adquirida en la comunidad",
        "fiebre": "Síndrome febril inespecífico",
        "dolor abdominal": "Gastroenteritis aguda",
        "diarrea": "Gastroenteritis aguda",
        "pecho": "Síndrome coronario agudo",
        "cefalea": "Migraña",
        "sangre heces": "Colitis ulcerosa (sospecha)",
        "ardor estómago": "Reflujo gastroesofágico",
        "ansiedad": "Ansiedad generalizada",
        "depresión": "Depresión mayor",
        "erupción": "Urticaria aguda"
    }
    for k, v in keywords.items():
        if k in t and v.lower() in ENF_IDX:
            return ENF_IDX[v.lower()]
    return None

def build_answer(user_text: str) -> str:
    triage = quick_triage(user_text)
    preface = triage + "\n\n" if triage else ""
    cond = match_condition(user_text)
    if cond:
        bullets = [
            f"**Posible condición (informativa):** {cond['nombre']}",
            f"**Qué es (en general):** {cond['descripcion']}",
            f"**Síntomas frecuentes:** {', '.join(cond.get('signos_sintomas', [])[:6]) or '—'}",
            f"**Exámenes sugeridos:** {', '.join(cond.get('examenes_sugeridos', [])[:6]) or '—'}",
            f"**Medidas generales:** {', '.join(cond.get('opciones_tratamiento_informativo', [])[:6]) or '—'}"
        ]
        return preface + "\n".join(bullets) + SAFETY_FOOTER
    return preface + (
        "Puedo darte orientación general basada en lo que describes. "
        "Cuéntame: ¿cuándo empezó, qué lo agrava/alivia, y si hay fiebre, dolor intenso, dificultad para respirar, "
        "debilidad, vómitos persistentes o sangrado? Con esos datos puedo orientarte mejor sobre posibles causas, "
        "señales de alarma y próximos pasos (consultas, exámenes o autocuidados seguros)."
    ) + SAFETY_FOOTER

@app.post("/api/message")
async def chat_message(payload: Dict[str, Any] = Body(...)):
    token = payload.get("token")
    message = (payload.get("message") or "").strip()
    if not token or token not in ACTIVE_TOKENS:
        raise HTTPException(401, "Sesión inválida o expirada.")
    if not message:
        raise HTTPException(400, "Mensaje vacío.")
    answer = build_answer(message)
    return {"reply": answer}

@app.get("/quick-response", response_class=HTMLResponse)
async def quick_response(request: Request):
    return templates.TemplateResponse("quick-response.html", {"request": request})
