# src/main.py
import os, json, stripe, secrets, time
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, Body, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import openai

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Monta la carpeta estática única
app.mount("/static", StaticFiles(directory="src/static"), name="static")

app = FastAPI()

# Configura tu API Key (usa variable de entorno en producción)
openai.api_key = "TU_API_KEY_AQUI"

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")  # Asegúrate de tener tu API Key

app = FastAPI()

# Permitir CORS para que tu frontend pueda llamar al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo para recibir mensajes
class MessageRequest(BaseModel):
    nickname: str
    message: str

# Almacén simple de conversaciones (en memoria)
conversations = {}

@app.post("/api/message")
async def handle_message(req: MessageRequest):
    user = req.nickname
    msg = req.message

    # Inicializa historial si no existe
    if user not in conversations:
        conversations[user] = []

    # Agrega mensaje del usuario al historial
    conversations[user].append({"role": "user", "content": msg})

    # Genera respuesta usando GPT
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversations[user],
            max_tokens=200
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Error al procesar tu mensaje: {str(e)}"

    # Agrega la respuesta al historial
    conversations[user].append({"role": "assistant", "content": reply})

    return {"reply": reply}


@app.post("/api/message")
async def send_message(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    if not user_message.strip():
        return JSONResponse({"reply": "Por favor escribe un mensaje."})

    try:
        # Llamada a OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente médico experto en risoterapia y bienestar natural."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_reply = response["choices"][0]["message"]["content"]

        return JSONResponse({"reply": bot_reply})

    except Exception as e:
        return JSONResponse({"reply": f"Error al conectar con el asistente: {str(e)}"})


# =========================
# Configuración y Stripe
# =========================
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
BASE_URL = os.getenv("BASE_URL", "https://medico-virtual-may-roga.onrender.com")
SECRET_FREE_CODE = os.getenv("SECRET_FREE_CODE", "MKM991775")  # <<— TU ENV
USE_AI = os.getenv("USE_AI", "0") == "1"  # si luego conectas IA real
stripe.api_key = STRIPE_SECRET_KEY

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# =========================
# Templates y static
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# =========================
# Memoria en servidor (simple)
# =========================
ACTIVE_TOKENS: Dict[str, Dict[str, Any]] = {}
PAID_NICKNAMES = set()

# =========================
# Carga de datos locales (opcional)
# =========================
def load_json_candidate(name):
    paths = [
        os.path.join(BASE_DIR, name),
        os.path.join(BASE_DIR, "..", name),
        os.path.join(BASE_DIR, "data", name),
    ]
    for p in paths:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return []

ENF = load_json_candidate("enfermedades.json")
URG = load_json_candidate("urgencias.json")
print("✅ Datos enfer/urgencias cargados:", bool(ENF), bool(URG))

ENF_IDX = {e.get("nombre","").lower(): e for e in ENF if isinstance(e, dict)}

# =========================
# Utilidades
# =========================
SAFETY_FOOTER = "\n\n—\nInformación educativa. No es diagnóstico médico. Si empeoran síntomas, acudir a urgencias."
EMERGENCY_SIGNS = ["dolor torácico","ahogo","disnea","debilidad","convulsión","sangrado","fiebre muy alta","pérdida de conciencia"]

def quick_triage(text: str) -> str | None:
    t = text.lower()
    for s in EMERGENCY_SIGNS:
        if s in t:
            return f"⚠️ Posibles signos de urgencia: '{s}'. Si es actual, acude a emergencias."
    return None

def match_condition(text: str) -> Dict[str, Any] | None:
    t = text.lower()
    for name, data in ENF_IDX.items():
        if all(word in t for word in name.split()[:1]):
            return data
    return None

def build_answer_local_asistente(text: str) -> str:
    triage = quick_triage(text)
    pre = triage + "\n\n" if triage else ""
    cond = match_condition(text)
    if cond:
        return pre + f"**Condición informativa:** {cond.get('nombre','—')}\n**Qué es:** {cond.get('descripcion','—')}\n{SAFETY_FOOTER}"
    return pre + "Guíame con tus síntomas: inicio, fiebre, intensidad del dolor, medicación tomada." + SAFETY_FOOTER

def build_answer_local_risoterapia(text: str) -> str:
    return "😄 ¡Gracias por escribir! Toma 3 respiraciones profundas. Piensa en 1 cosa buena de hoy. Repite: “Puedo con esto”. ¿Qué te gustaría mejorar ahora mismo?"

def build_answer_local_horoscopo(text: str) -> str:
    return "✨ Horóscopo express: confía en tu intuición hoy, evita decisiones impulsivas y prioriza tu paz mental."

def build_answer_local_quick(text: str) -> str:
    triage = quick_triage(text)
    pre = (triage + " ") if triage else ""
    return pre + "Consulta rápida recibida. Si puedes, añade edad, tiempo de inicio y síntomas clave."

# =========================
# Página raíz
# =========================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, paid: str | None = None, nickname: str | None = None):
    return templates.TemplateResponse("index.html", {"request": request, "paid": paid, "nickname": nickname})

# =========================
# Redirección legacy
# =========================
@app.get("/quick-response")
async def redirect_quick_response():
    return RedirectResponse(url="/quickresponse")

# =========================
# Vistas (HTML) de cada servicio
# =========================
def _token_from_query(nickname: str | None, code: str | None):
    """
    Si viene nickname + código secreto válido o nickname ya pagado,
    se emite token. Si no, no hay token (solo vista).
    """
    token = None
    if nickname:
        if code and secrets.compare_digest(code, SECRET_FREE_CODE):
            token = secrets.token_urlsafe(32)
            ACTIVE_TOKENS[token] = {"nickname": nickname, "created": time.time(), "paid": True, "free": True}
        elif nickname in PAID_NICKNAMES:
            token = secrets.token_urlsafe(32)
            ACTIVE_TOKENS[token] = {"nickname": nickname, "created": time.time(), "paid": True, "free": False}
    return token

@app.get("/asistente", response_class=HTMLResponse)
async def asistente_view(request: Request, nickname: str | None = None, code: str | None = None):
    token = _token_from_query(nickname, code)
    return templates.TemplateResponse("asistente.html", {"request": request, "nickname": nickname, "token": token})

@app.get("/risoterapia", response_class=HTMLResponse)
async def risoterapia_view(request: Request, nickname: str | None = None, code: str | None = None):
    token = _token_from_query(nickname, code)
    return templates.TemplateResponse("risoterapia.html", {"request": request, "nickname": nickname, "token": token})

@app.get("/horoscopo", response_class=HTMLResponse)
async def horoscopo_view(request: Request, nickname: str | None = None, code: str | None = None):
    token = _token_from_query(nickname, code)
    return templates.TemplateResponse("horoscopo.html", {"request": request, "nickname": nickname, "token": token})

@app.get("/quickresponse", response_class=HTMLResponse)
async def quickresponse_view(request: Request, nickname: str | None = None, code: str | None = None):
    token = _token_from_query(nickname, code)
    return templates.TemplateResponse("quickresponse.html", {"request": request, "nickname": nickname, "token": token})

# =========================
# Sesiones / acceso explícito (form o fetch)
# =========================
@app.post("/api/start-session")
async def start_session(payload: Dict[str, Any] = Body(...)):
    nickname = (payload.get("nickname") or "").strip()
    code = (payload.get("code") or "").strip()
    if not nickname:
        raise HTTPException(400, "Apodo obligatorio.")

    if code and secrets.compare_digest(code, SECRET_FREE_CODE):
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
# Stripe: Crear checkout (opcional)
# =========================
@app.api_route("/pay/create-session", methods=["GET", "POST"])
async def create_session(request: Request):
    if request.method == "POST":
        form = await request.form()
        nickname = (form.get("nickname") or "").strip()
        servicio = (form.get("servicio") or "").strip()
        price_cents = form.get("price_cents")
    else:
        qs = request.query_params
        nickname = (qs.get("nickname") or "").strip()
        servicio = (qs.get("servicio") or "").strip()
        price_cents = qs.get("price_cents")

    if not nickname:
        raise HTTPException(400, "Debes indicar un apodo.")

    prices = {"asistente":500, "risoterapia":1200, "horoscopo":300, "quick":100}
    try:
        amount = int(price_cents) if price_cents else prices.get(servicio, int(os.getenv("PRICE_USD_CENTS","1500")))
    except Exception:
        amount = prices.get(servicio, int(os.getenv("PRICE_USD_CENTS","1500")))

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            client_reference_id=nickname,
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Médico Virtual May Roga - {servicio or 'sesión'}"},
                    "unit_amount": int(amount)
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
# Webhook Stripe (confirma pagos)
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
# ENDPOINTS DE MENSAJE (funcionan ya)
# Requieren: token válido y message
# =========================
def _require_token_and_message(payload: Dict[str, Any]):
    token = payload.get("token")
    message = (payload.get("message") or "").strip()
    if not token or token not in ACTIVE_TOKENS:
        raise HTTPException(401, "Sesión inválida o expirada (token).")
    if not message:
        raise HTTPException(400, "Mensaje vacío.")
    return token, message

@app.post("/api/asistente")
async def api_asistente(payload: Dict[str, Any] = Body(...)):
    _, message = _require_token_and_message(payload)
    if USE_AI:
        reply = f"[AI-Asistente] {message}"
    else:
        reply = build_answer_local_asistente(message)
    return {"reply": reply}

@app.post("/api/risoterapia")
async def api_risoterapia(payload: Dict[str, Any] = Body(...)):
    _, message = _require_token_and_message(payload)
    if USE_AI:
        reply = f"[AI-Risoterapia] {message}"
    else:
        reply = build_answer_local_risoterapia(message)
    return {"reply": reply}

@app.post("/api/horoscopo")
async def api_horoscopo(payload: Dict[str, Any] = Body(...)):
    _, message = _require_token_and_message(payload)
    if USE_AI:
        reply = f"[AI-Horóscopo] {message}"
    else:
        reply = build_answer_local_horoscopo(message)
    return {"reply": reply}

@app.post("/api/quickresponse")
async def api_quickresponse(payload: Dict[str, Any] = Body(...)):
    _, message = _require_token_and_message(payload)
    if USE_AI:
        reply = f"[AI-Quick] {message}"
    else:
        reply = build_answer_local_quick(message)
    return {"reply": reply}

# =========================
# Arranque local
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)

from fastapi import Request
from fastapi.responses import JSONResponse
import openai
import os

# Asegúrate de tener la variable de entorno OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/api/message")
async def send_message(request: Request):
    """
    Endpoint para recibir un mensaje del cliente y responder usando OpenAI.
    """
    data = await request.json()
    nickname = data.get("nickname")
    message = data.get("message")

    if not nickname or not message:
        return JSONResponse({"error": "Falta nickname o mensaje"}, status_code=400)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres el asistente médico May Roga, profesional en risoterapia y bienestar natural."},
                {"role": "user", "content": message}
            ]
        )
        reply = response['choices'][0]['message']['content']
        return {"reply": reply}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import openai  # Asegúrate de tener la variable OPENAI_API_KEY en tu entorno

app = FastAPI()

# Inicializa OpenAI con tu API Key
openai.api_key = "TU_OPENAI_API_KEY"

@app.post("/api/message")
async def receive_message(request: Request):
    data = await request.json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return JSONResponse({"reply": "No recibí ningún mensaje."})

    try:
        # Llamada al modelo de OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7
        )
        reply_text = response.choices[0].message.content.strip()
        return JSONResponse({"reply": reply_text})
    except Exception as e:
        return JSONResponse({"reply": f"Ocurrió un error: {str(e)}"})
