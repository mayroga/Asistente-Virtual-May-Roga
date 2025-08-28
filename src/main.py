import os
import time
from typing import Dict, Any
from fastapi import FastAPI, Request, Form, HTTPException, Header
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import stripe

# ========= CONFIG =========
SECRET_CODE_NAME = os.getenv("SECRET_CODE_NAME", "MKM991775")  # tu código maestro
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")               # si no está, usamos fallback
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")         # obliga a ponerlo en Render
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "") # opcional, solo si usas webhook

stripe.api_key = STRIPE_SECRET_KEY

# ========= APP =========
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# CORS abierto por sencillez (ajusta dominios si quieres)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========= ESTADO EN MEMORIA =========
# Accesos concedidos por apodo: {"apodo": {"granted": True, "via": "secret|stripe", "ts": 12345}}
ACCESS_DB: Dict[str, Dict[str, Any]] = {}

# Servicios y precios (en centavos USD para Stripe)
SERVICES = {
    "asistente_virtual": {"titulo": "Asistente Virtual Médico", "minutos": 8, "cents": 500},
    "risoterapia": {"titulo": "Risoterapia y Bienestar Natural", "minutos": 10, "cents": 1200},
    "horoscopo": {"titulo": "Horóscopo", "minutos": 1, "cents": 300},
}

# ========= UTIL =========
def build_base_url(request: Request) -> str:
    # Render envía x-forwarded-proto y host
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    return f"{scheme}://{host}"

def grant_access(nick: str, via: str):
    ACCESS_DB[nick] = {"granted": True, "via": via, "ts": int(time.time())}

# ========= RUTAS =========
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "services": SERVICES,
            "secret_enabled": True,  # para mostrar el bloque de código secreto
        },
    )

@app.post("/access-secret")
async def access_secret(apodo: str = Form(...), codigo: str = Form(...)):
    if not apodo.strip():
        raise HTTPException(status_code=400, detail="Apodo requerido.")
    if codigo.strip().lower() == SECRET_CODE_NAME.lower():
        grant_access(apodo.strip(), "secret")
        return {"ok": True, "message": f"Acceso concedido para {apodo} vía código."}
    return {"ok": False, "message": "Código incorrecto."}

@app.post("/create-checkout-session")
async def create_checkout_session(request: Request,
                                  apodo: str = Form(...),
                                  servicio: str = Form(...)):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=400, detail="Stripe no está configurado en el servidor.")

    if servicio not in SERVICES:
        raise HTTPException(status_code=400, detail="Servicio inválido.")

    base_url = build_base_url(request)
    success_url = f"{base_url}/success?apodo={apodo}&servicio={servicio}"
    cancel_url = f"{base_url}/?cancel=1"

    svc = SERVICES[servicio]
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"{svc['titulo']} — {svc['minutos']} min"},
                    "unit_amount": svc["cents"],
                },
                "quantity": 1,
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"apodo": apodo, "servicio": servicio},
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/success", response_class=HTMLResponse)
async def success(request: Request, apodo: str, servicio: str):
    # Marcamos acceso por pago (simple; el webhook podría reforzar)
    grant_access(apodo, "stripe")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "services": SERVICES,
            "secret_enabled": True,
            "success": True,
            "apodo": apodo,
            "servicio": servicio,
        },
    )

# Webhook (opcional, si lo configuras en Stripe Dashboard)
@app.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    if not STRIPE_WEBHOOK_SECRET:
        # Si no tienes webhook secret configurado, ignora tranquilo
        return PlainTextResponse("webhook not configured", status_code=200)

    payload = await request.body()
    sig_header = stripe_signature or request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return PlainTextResponse(str(e), status_code=400)

    # Marca acceso cuando un pago sea exitoso (seguridad adicional)
    if event["type"] == "checkout.session.completed":
        sess = event["data"]["object"]
        apodo = (sess.get("metadata") or {}).get("apodo")
        if apodo:
            grant_access(apodo, "stripe")

    return PlainTextResponse("ok", status_code=200)

# Chat — requiere acceso concedido
@app.post("/chat")
async def chat(apodo: str = Form(...), message: str = Form(...), servicio: str = Form("asistente_virtual")):
    apodo = (apodo or "").strip()
    if not apodo:
        raise HTTPException(status_code=400, detail="Apodo requerido.")
    if apodo not in ACCESS_DB or not ACCESS_DB[apodo]["granted"]:
        return {"ok": False, "respuesta": "Acceso no autorizado. Usa apodo+código o apodo+pago."}

    # Selección de “rol”/tono por servicio
    tone = {
        "asistente_virtual": "Eres un asistente virtual médico informativo. No hagas diagnóstico; da orientación general y señales de alarma. Pide edad aproximada, duración y síntomas clave.",
        "risoterapia": "Eres un coach de risoterapia y bienestar natural de May Roga LLC. Entregas ejercicios breves, respiración, humor ligero seguro y hábitos saludables.",
        "horoscopo": "Actúa como un horóscopo breve y positivo (35-60 segundos de lectura aproximada). Sé entretenido pero no determinista.",
    }.get(servicio, "Eres un asistente útil y conciso.")

    # ===== OpenAI si hay clave; si no, fallback offline =====
    try:
        if OPENAI_API_KEY:
            # OpenAI SDK >= 1.0
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": tone},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
            )
            text = completion.choices[0].message.content.strip()
        else:
            # Fallback simple offline
            text = (
                f"({servicio.upper()}) Respuesta para '{apodo}': recibí tu mensaje: '{message}'. "
                "Servicio informativo. Si hay urgencia, busca atención presencial."
            )
        return {"ok": True, "respuesta": text}
    except Exception as e:
        # Fallback si OpenAI falla
        text = (
            f"({servicio.upper()}) Respuesta para '{apodo}': recibí tu mensaje: '{message}'. "
            "Por ahora respondo en modo básico. Si hay urgencia, atención presencial."
        )
        return {"ok": True, "respuesta": text}

# ====== Servir el JS sin carpeta /static (evita errores en Render) ======
SCRIPT_JS = r"""
/* ======= FRONTEND JS ======= */
function $(id){return document.getElementById(id);}

async function postForm(url, data){
  const res = await fetch(url,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:new URLSearchParams(data)});
  if(!res.ok){ const t=await res.text(); throw new Error(t); }
  return await res.json();
}

document.addEventListener("DOMContentLoaded", () => {
  const secretForm = $("secret-form");
  const payForm = $("pay-form");
  const chatForm = $("chat-form");

  // Acceso por código
  if(secretForm){
    secretForm.addEventListener("submit", async (e)=>{
      e.preventDefault();
      const apodo = $("apodo_secret").value.trim();
      const codigo = $("codigo_secret").value.trim();
      if(!apodo){ alert("Ingresa apodo"); return; }
      if(!codigo){ alert("Ingresa el código secreto"); return; }
      try{
        const data = await postForm("/access-secret", {apodo, codigo});
        if(data.ok){
          $("access-status").innerText = `Acceso concedido para ${apodo}.`;
          $("apodo_chat").value = apodo;
          $("apodo_pay").value = apodo;
        }else{
          alert(data.message || "Código incorrecto");
        }
      }catch(err){
        alert("Error de servidor al validar código.");
      }
    });
  }

  // Pago Stripe
  if(payForm){
    payForm.addEventListener("submit", async (e)=>{
      e.preventDefault();
      const apodo = $("apodo_pay").value.trim();
      const servicio = $("servicio").value;
      if(!apodo){ alert("Ingresa apodo antes de pagar."); return; }
      try{
        const data = await postForm("/create-checkout-session", {apodo, servicio});
        if(data.url){ window.location.href = data.url; }
        else{ alert("No se pudo iniciar el pago."); }
      }catch(err){
        alert("Error al iniciar pago.");
      }
    });
  }

  // Chat
  if(chatForm){
    chatForm.addEventListener("submit", async (e)=>{
      e.preventDefault();
      const apodo = $("apodo_chat").value.trim();
      const servicio = $("servicio_chat").value;
      const message = $("message").value.trim();
      if(!apodo){ alert("Ingresa apodo para chatear."); return; }
      if(!message){ return; }
      $("sendBtn").disabled = true;
      $("sendBtn").innerText = "Enviando...";
      try{
        const data = await postForm("/chat", {apodo, servicio, message});
        const box = $("chat-box");
        if(data.ok){
          box.value += `${apodo}: ${message}\nAsistente: ${data.respuesta}\n\n`;
        }else{
          box.value += `⚠️ ${data.respuesta}\n\n`;
        }
        $("message").value = "";
      }catch(err){
        alert("Error al enviar mensaje.");
      }finally{
        $("sendBtn").disabled = false;
        $("sendBtn").innerText = "Enviar";
      }
    });

    $("clearBtn").addEventListener("click", ()=>{
      $("chat-box").value = "";
    });
  }
});
"""

@app.get("/script.js")
async def script_js():
    return Response(content=SCRIPT_JS, media_type="application/javascript")
